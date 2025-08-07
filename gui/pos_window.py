# gui/pos_window.py
import tkinter as tk
from tkinter import ttk, messagebox, TclError
from datetime import datetime
from database.database import db_manager, DatabaseUtils
from database.models import Product, Sale, SaleItem, Customer, StockMovement
from utils.auth import get_current_user
from utils.i18n import translate as _
from sqlalchemy import func

class POSWindow:
    def __init__(self, parent):
        self.parent = parent
        self.cart_items = []
        self.selected_customer = None

        # Create main POS interface
        self.setup_ui()
        self.load_products()
        self.load_customers()
        self.inventory_binding = self.parent.bind('<<InventoryChanged>>', self.on_inventory_changed)
        self.dashboard_job = None
        self.update_dashboard()
        
    def setup_ui(self):
        """Setup POS user interface"""
        # Main container
        main_container = ttk.PanedWindow(self.parent, orient=tk.HORIZONTAL)
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Left panel - Product search and selection
        self.left_panel = ttk.Frame(main_container)
        main_container.add(self.left_panel, weight=2)
        
        # Right panel - Cart and checkout
        self.right_panel = ttk.Frame(main_container)
        main_container.add(self.right_panel, weight=1)
        
        self.setup_left_panel()
        self.setup_right_panel()
    
    def setup_left_panel(self):
        """Setup left panel with product search and grid"""
        # Search section
        search_frame = ttk.LabelFrame(self.left_panel, text=_('product_search'), padding="10")
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text=f"{_('search')}:").grid(row=0, column=0, sticky=tk.W)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=('Arial', 12))
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        search_entry.focus()
        
        # Category filter
        ttk.Label(search_frame, text=f"{_('category')}:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(search_frame, textvariable=self.category_var, state="readonly")
        self.category_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=(5, 0))
        self.category_combo.bind('<<ComboboxSelected>>', self.on_category_change)
        
        # Products grid
        products_frame = ttk.LabelFrame(self.left_panel, text=_('products'), padding="5")
        products_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        products_frame.columnconfigure(0, weight=1)
        products_frame.rowconfigure(0, weight=1)
        
        # Products treeview
        columns = ('ID', 'Name', 'Category', 'Price', 'Stock', 'Unit')
        self.products_tree = ttk.Treeview(products_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        self.products_tree.heading('ID', text=_('id'))
        self.products_tree.heading('Name', text=_('name'))
        self.products_tree.heading('Category', text=_('category'))
        self.products_tree.heading('Price', text=_('price'))
        self.products_tree.heading('Stock', text=_('stock'))
        self.products_tree.heading('Unit', text=_('unit'))
        
        # Define column widths
        self.products_tree.column('ID', width=50, anchor='center')
        self.products_tree.column('Name', width=250)
        self.products_tree.column('Category', width=120)
        self.products_tree.column('Price', width=80, anchor='e')
        self.products_tree.column('Stock', width=70, anchor='center')
        self.products_tree.column('Unit', width=70, anchor='center')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(products_frame, orient=tk.VERTICAL, command=self.products_tree.yview)
        h_scrollbar = ttk.Scrollbar(products_frame, orient=tk.HORIZONTAL, command=self.products_tree.xview)
        self.products_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.products_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Double-click to add to cart
        self.products_tree.bind('<Double-1>', self.add_to_cart)
        
        # Add to cart button
        add_button = ttk.Button(products_frame, text=_('add_to_cart'), command=self.add_to_cart)
        add_button.grid(row=2, column=0, pady=10)

        # Configure grid weights
        self.left_panel.columnconfigure(0, weight=1)
        self.left_panel.rowconfigure(1, weight=1)

        # Dashboard frame for quick stats
        dashboard_frame = ttk.LabelFrame(self.left_panel, text=_('dashboard'), padding="5")
        dashboard_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        ttk.Label(dashboard_frame, text=_("total_sales")).grid(row=0, column=0, sticky=tk.W)
        self.total_sales_var = tk.StringVar(value="0")
        ttk.Label(dashboard_frame, textvariable=self.total_sales_var).grid(row=0, column=1, sticky=tk.W)

        ttk.Label(dashboard_frame, text=_("revenue")).grid(row=1, column=0, sticky=tk.W)
        self.revenue_var = tk.StringVar(value="0")
        ttk.Label(dashboard_frame, textvariable=self.revenue_var).grid(row=1, column=1, sticky=tk.W)

        ttk.Label(dashboard_frame, text=_("low_stock")).grid(row=2, column=0, sticky=tk.W)
        self.low_stock_var = tk.StringVar(value="0")
        ttk.Label(dashboard_frame, textvariable=self.low_stock_var).grid(row=2, column=1, sticky=tk.W)
    
    def setup_right_panel(self):
        """Setup right panel with cart and checkout"""
        # Customer selection
        customer_frame = ttk.LabelFrame(self.right_panel, text=_('customer_label'), padding="10")
        customer_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        customer_frame.columnconfigure(1, weight=1)
        
        ttk.Label(customer_frame, text=f"{ _('customer') }:").grid(row=0, column=0, sticky=tk.W)
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(customer_frame, textvariable=self.customer_var, state="normal")
        self.customer_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        # Shopping cart
        cart_frame = ttk.LabelFrame(self.right_panel, text=_('shopping_cart'), padding="5")
        cart_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        cart_frame.columnconfigure(0, weight=1)
        cart_frame.rowconfigure(0, weight=1)
        
        # Cart treeview
        cart_columns = ('Product', 'Qty', 'Price', 'Total')
        self.cart_tree = ttk.Treeview(cart_frame, columns=cart_columns, show='headings', height=10)

        self.cart_tree.heading('Product', text=_('shopping_cart_product'))
        self.cart_tree.heading('Qty', text=_('qty'))
        self.cart_tree.heading('Price', text=_('price'))
        self.cart_tree.heading('Total', text=_('total'))
        
        self.cart_tree.column('Product', width=150)
        self.cart_tree.column('Qty', width=60, anchor='center')
        self.cart_tree.column('Price', width=80, anchor='e')
        self.cart_tree.column('Total', width=80, anchor='e')
        
        cart_scrollbar = ttk.Scrollbar(cart_frame, orient=tk.VERTICAL, command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=cart_scrollbar.set)
        
        self.cart_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        cart_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Cart buttons
        cart_buttons_frame = ttk.Frame(cart_frame)
        cart_buttons_frame.grid(row=1, column=0, columnspan=2, pady=5)
        
        ttk.Button(cart_buttons_frame, text=_('edit_qty'), command=self.edit_quantity).grid(row=0, column=0, padx=2)
        ttk.Button(cart_buttons_frame, text=_('remove'), command=self.remove_from_cart).grid(row=0, column=1, padx=2)
        ttk.Button(cart_buttons_frame, text=_('clear_all'), command=self.clear_cart).grid(row=0, column=2, padx=2)
        
        # Totals section
        totals_frame = ttk.LabelFrame(self.right_panel, text=_('order_total'), padding="10")
        totals_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        totals_frame.columnconfigure(1, weight=1)
        
        # Total labels
        ttk.Label(totals_frame, text=_('subtotal_label')).grid(row=0, column=0, sticky=tk.W)
        self.subtotal_label = ttk.Label(totals_frame, text="0.00", font=('Arial', 12, 'bold'))
        self.subtotal_label.grid(row=0, column=1, sticky=tk.E)

        ttk.Label(totals_frame, text=f"{ _('tax_rate') }:").grid(row=1, column=0, sticky=tk.W)
        self.tax_rate_var = tk.StringVar(value=DatabaseUtils.get_setting_value('tax_rate', '0'))
        ttk.Entry(totals_frame, textvariable=self.tax_rate_var, width=10).grid(row=1, column=1, sticky=tk.E)
        self.tax_rate_var.trace('w', lambda *args: self.calculate_totals())

        ttk.Label(totals_frame, text=f"{ _('tax_amount') }:").grid(row=2, column=0, sticky=tk.W)
        self.tax_label = ttk.Label(totals_frame, text="0.00")
        self.tax_label.grid(row=2, column=1, sticky=tk.E)


        ttk.Label(totals_frame, text=f"{ _('total_label') }").grid(row=3, column=0, sticky=tk.W)

        ttk.Label(totals_frame, text=f"{ _('total') }:").grid(row=3, column=0, sticky=tk.W)

        self.total_label = ttk.Label(totals_frame, text="0.00", font=('Arial', 14, 'bold'))
        self.total_label.grid(row=3, column=1, sticky=tk.E)
        
        # Payment section
        payment_frame = ttk.LabelFrame(self.right_panel, text=_('payment'), padding="10")
        payment_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        payment_frame.columnconfigure(1, weight=1)
        
        ttk.Label(payment_frame, text=_('payment_method_label')).grid(row=0, column=0, sticky=tk.W)
        self.payment_var = tk.StringVar(value="cash")
        payment_combo = ttk.Combobox(payment_frame, textvariable=self.payment_var, 
                                   values=["cash", "card", "credit"], state="readonly")
        payment_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        ttk.Label(payment_frame, text=_('amount_paid_label')).grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.paid_var = tk.StringVar()
        self.paid_entry = ttk.Entry(payment_frame, textvariable=self.paid_var)
        self.paid_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=(5, 0))
        self.paid_entry.bind('<KeyRelease>', self.calculate_change)
        
        ttk.Label(payment_frame, text=_('change_label')).grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.change_label = ttk.Label(payment_frame, text="0.00", font=('Arial', 12, 'bold'))
        self.change_label.grid(row=2, column=1, sticky=tk.E, pady=(5, 0))
        
        # Checkout buttons
        checkout_frame = ttk.Frame(self.right_panel)
        checkout_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), padx=5, pady=10)
        checkout_frame.columnconfigure(0, weight=1)
        checkout_frame.columnconfigure(1, weight=1)
        
        ttk.Button(checkout_frame, text=_('process_sale'), command=self.process_sale,
                  style='Large.TButton').grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Button(checkout_frame, text=_('hold_sale'), command=self.hold_sale).grid(row=1, column=0, sticky=(tk.W, tk.E), padx=(0, 2))
        ttk.Button(checkout_frame, text=_('new_sale'), command=self.new_sale).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(2, 0))
        
        # Configure grid weights
        self.right_panel.columnconfigure(0, weight=1)
        self.right_panel.rowconfigure(1, weight=1)
    
    def load_products(self):
        """Load products from database"""
        session = db_manager.get_session()
        try:
            from database.models import Category

            # Load categories for filter
            categories = session.query(Category).all()
            category_names = ["All Categories"] + [cat.name for cat in categories]
            try:
                self.category_combo['values'] = category_names
                self.category_combo.set("All Categories")
            except TclError:
                return

            # Load products
            self.refresh_products()

        except Exception as e:
            messagebox.showerror(_("error"), f"{_('failed_load_products')}: {e}")
        finally:
            session.close()
    
    def refresh_products(self, search_term="", category_filter="All Categories"):
        """Refresh products list based on search and filter"""
        session = db_manager.get_session()
        try:
            # Clear existing items
            for item in self.products_tree.get_children():
                self.products_tree.delete(item)
            
            # Build query
            query = session.query(Product).filter(Product.is_active == True)
            
            # Apply search filter
            if search_term:
                query = query.filter(
                    Product.name.contains(search_term) | 
                    Product.barcode.contains(search_term)
                )
            
            # Apply category filter
            if category_filter != "All Categories":
                from database.models import Category
                category = session.query(Category).filter(Category.name == category_filter).first()
                if category:
                    query = query.filter(Product.category_id == category.id)
            
            products = query.all()
            
            # Populate treeview
            for product in products:
                category_name = product.category.name if product.category else "N/A"
                values = (
                    product.id,
                    product.name,
                    category_name,
                    f"{product.selling_price:,.0f}",
                    product.stock_quantity,
                    product.unit
                )
                self.products_tree.insert('', tk.END, values=values)
                
        except Exception as e:
            messagebox.showerror(_("error"), f"{_('failed_refresh_products')}: {e}")
        finally:
            session.close()
    
    def load_customers(self):
        """Load customers for selection"""
        session = db_manager.get_session()
        try:
            customers = session.query(Customer).filter(Customer.is_active == True).all()
            customer_names = [f"{c.id} - {c.name}" for c in customers]
            self.customer_combo['values'] = customer_names
            
            # Select default customer (Walk-in)
            if customer_names:
                self.customer_combo.set(customer_names[0])
                
        except Exception as e:
            messagebox.showerror(_("error"), f"{_('failed_load_customers')}: {e}")
        finally:
            session.close()

    def update_dashboard(self):
        """Update dashboard statistics"""
        session = db_manager.get_session()
        try:
            total_sales = session.query(func.count(Sale.id)).scalar() or 0
            revenue = session.query(func.sum(Sale.total_amount)).scalar() or 0
            low_stock = session.query(func.count(Product.id)).filter(
                Product.is_active == True,
                Product.stock_quantity <= Product.min_stock_level
            ).scalar() or 0

            currency = DatabaseUtils.get_setting_value('currency', 'FCFA')
            self.total_sales_var.set(str(total_sales))
            self.revenue_var.set(f"{revenue:,.0f} {currency}")
            self.low_stock_var.set(str(low_stock))
        finally:
            session.close()

        # Schedule periodic refresh
        try:
            self.dashboard_job = self.parent.after(60000, self.update_dashboard)
        except Exception:
            self.dashboard_job = None

    def on_inventory_changed(self, event=None):
        """Handle inventory updates from other windows"""
        self.load_products()
        self.update_dashboard()
    
    def on_search_change(self, *args):
        """Handle search text change"""
        search_term = self.search_var.get()
        category = self.category_var.get()
        self.refresh_products(search_term, category)
    
    def on_category_change(self, event):
        """Handle category filter change"""
        search_term = self.search_var.get()
        category = self.category_var.get()
        self.refresh_products(search_term, category)
    
    def add_to_cart(self, event=None):
        """Add selected product to cart"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning(_("no_selection"), _("select_product"))
            return
        
        item = self.products_tree.item(selection[0])
        product_id = item['values'][0]
        product_name = item['values'][1]
        price = float(item['values'][3].replace(',', ''))
        stock = int(item['values'][4])
        unit = item['values'][5]
        
        if stock <= 0:
            messagebox.showwarning(_("out_of_stock"), _("out_of_stock_msg").format(product_name))
            return
        
        # Ask for quantity
        quantity = self.ask_quantity(product_name, stock, unit)
        if quantity is None or quantity <= 0:
            return
        
        if quantity > stock:
            messagebox.showwarning(_("insufficient_stock_title"),
                                 _("insufficient_stock").format(stock, unit, product_name))
            return
        
        # Check if product already in cart
        for i, cart_item in enumerate(self.cart_items):
            if cart_item['product_id'] == product_id:
                # Update quantity
                new_qty = cart_item['quantity'] + quantity
                if new_qty > stock:
                    messagebox.showwarning(_("insufficient_stock_title"),
                                         f"Total quantity would exceed available stock ({stock}).")
                    return
                cart_item['quantity'] = new_qty
                cart_item['total'] = new_qty * price
                break
        else:
            # Add new item to cart
            cart_item = {
                'product_id': product_id,
                'name': product_name,
                'quantity': quantity,
                'price': price,
                'total': quantity * price,
                'unit': unit
            }
            self.cart_items.append(cart_item)
        
        self.refresh_cart()
        self.calculate_totals()
    
    def ask_quantity(self, product_name, max_stock, unit):
        """Ask user for quantity"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(_("enter_quantity"))
        dialog.geometry("400x200")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("400x200+{}+{}".format(
            self.parent.winfo_rootx() + 50,
            self.parent.winfo_rooty() + 50
        ))
        
        result = {'quantity': None}
        
        ttk.Label(dialog, text=f"{_('product_label')}: {product_name}").pack(pady=10)
        ttk.Label(dialog, text=f"{_('available')}: {max_stock} {unit}(s)").pack()

        ttk.Label(dialog, text=f"{_('quantity')}:").pack(pady=(10, 5))
        qty_var = tk.StringVar(value="1")
        qty_entry = ttk.Entry(dialog, textvariable=qty_var, width=10)
        qty_entry.pack()
        qty_entry.select_range(0, tk.END)
        qty_entry.focus()
        
        def ok_clicked():
            try:
                qty = float(qty_var.get())
                if qty > 0:
                    result['quantity'] = qty
                    dialog.destroy()
                else:
                    messagebox.showwarning("Invalid Quantity", "Quantity must be greater than 0.")
            except ValueError:
                messagebox.showwarning("Invalid Quantity", "Please enter a valid number.")
        
        def cancel_clicked():
            dialog.destroy()
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="OK", command=ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key
        qty_entry.bind('<Return>', lambda e: ok_clicked())
        
        dialog.wait_window()
        return result['quantity']
    
    def refresh_cart(self):
        """Refresh cart display"""
        # Clear cart tree
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        # Add cart items
        for item in self.cart_items:
            values = (
                item['name'][:20] + "..." if len(item['name']) > 20 else item['name'],
                f"{item['quantity']:.1f}",
                f"{item['price']:,.0f}",
                f"{item['total']:,.0f}"
            )
            self.cart_tree.insert('', tk.END, values=values)
    
    def calculate_totals(self):
        """Calculate and display totals"""
        subtotal = sum(item['total'] for item in self.cart_items)
        
        # Get tax rate from user input
        tax_rate = float(self.tax_rate_var.get() or 0)
        tax_amount = subtotal * (tax_rate / 100)
        total = subtotal + tax_amount
        
        # Update labels
        currency = DatabaseUtils.get_setting_value('currency', 'FCFA')
        self.subtotal_label.config(text=f"{subtotal:,.0f} {currency}")
        self.tax_label.config(text=f"{tax_amount:,.0f} {currency}")
        self.total_label.config(text=f"{total:,.0f} {currency}")
        
        # Auto-fill payment amount for cash
        if self.payment_var.get() == "cash":
            self.paid_var.set(f"{total:.0f}")
        
        self.calculate_change()
    
    def calculate_change(self, event=None):
        """Calculate change amount"""
        try:
            total = sum(item['total'] for item in self.cart_items)
            tax_rate = float(self.tax_rate_var.get() or 0)
            total_with_tax = total * (1 + tax_rate / 100)
            
            paid = float(self.paid_var.get() or 0)
            change = paid - total_with_tax
            
            currency = DatabaseUtils.get_setting_value('currency', 'FCFA')
            self.change_label.config(text=f"{change:,.0f} {currency}")
            
            if change < 0:
                self.change_label.config(foreground='red')
            else:
                self.change_label.config(foreground='black')
                
        except ValueError:
            self.change_label.config(text="0.00")
    
    def edit_quantity(self):
        """Edit quantity of selected cart item"""
        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item to edit.")
            return
        
        item_index = self.cart_tree.index(selection[0])
        cart_item = self.cart_items[item_index]
        
        # Get available stock
        session = db_manager.get_session()
        try:
            product = session.query(Product).get(cart_item['product_id'])
            if not product:
                messagebox.showerror(_("error"), _("failed_refresh_products"))
                return
            
            # Available stock includes current cart quantity
            available_stock = product.stock_quantity + cart_item['quantity']
            
            new_qty = self.ask_quantity(cart_item['name'], available_stock, cart_item['unit'])
            if new_qty is None or new_qty <= 0:
                return
            
            if new_qty > available_stock:
                messagebox.showwarning(_("insufficient_stock_title"),
                                     _("insufficient_stock").format(available_stock, cart_item['unit'], cart_item['name']))
                return
            
            # Update cart item
            cart_item['quantity'] = new_qty
            cart_item['total'] = new_qty * cart_item['price']
            
            self.refresh_cart()
            self.calculate_totals()
            
        except Exception as e:
            messagebox.showerror(_("error"), f"Failed to edit quantity: {e}")
        finally:
            session.close()
    
    def remove_from_cart(self):
        """Remove selected item from cart"""
        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showwarning(_("no_selection"), _("select_product"))
            return
        
        item_index = self.cart_tree.index(selection[0])
        del self.cart_items[item_index]
        
        self.refresh_cart()
        self.calculate_totals()
    
    def clear_cart(self):
        """Clear all items from cart"""
        if self.cart_items and messagebox.askyesno(_("clear_cart"), _("confirm_clear_cart")):
            self.cart_items.clear()
            self.refresh_cart()
            self.calculate_totals()
    
    def process_sale(self):
        """Process the current sale"""
        if not self.cart_items:
            messagebox.showwarning("Empty Cart", "Please add items to cart before processing sale.")
            return
        
        # Validate payment
        try:
            total = sum(item['total'] for item in self.cart_items)
            tax_rate = float(self.tax_rate_var.get() or 0)
            tax_amount = total * (tax_rate / 100)
            total_with_tax = total + tax_amount

            paid = float(self.paid_var.get() or 0)

            if self.payment_var.get() == "cash" and paid < total_with_tax:
                messagebox.showwarning("Insufficient Payment", "Payment amount is less than total.")
                return

        except ValueError:
            messagebox.showwarning("Invalid Payment", "Please enter a valid payment amount.")
            return

        # Determine customer (existing or new)
        customer_text = self.customer_var.get().strip()
        session = db_manager.get_session()
        try:
            if customer_text and ' - ' in customer_text and customer_text.split(' - ')[0].isdigit():
                customer_id = int(customer_text.split(' - ')[0])
            else:
                if not customer_text:
                    next_num = session.query(func.count(Customer.id)).scalar() + 1
                    customer_text = f"Customer {next_num}"
                customer = Customer(name=customer_text)
                session.add(customer)
                session.commit()
                customer_id = customer.id
        except Exception as e:
            session.rollback()
            messagebox.showerror("Customer Error", f"Failed to save customer: {e}")
            return
        finally:
            session.close()

        # Process sale in database
        session = db_manager.get_session()
        try:
            # Create sale record
            current_user = get_current_user()
            sale = Sale(
                sale_number=DatabaseUtils.generate_sale_number(),
                customer_id=customer_id,
                subtotal=total,
                tax_amount=tax_amount,
                total_amount=total_with_tax,
                payment_method=self.payment_var.get(),
                payment_status="paid",
                amount_paid=paid,
                change_amount=max(0, paid - total_with_tax),
                user_id=current_user.id if current_user else None,
            )
            session.add(sale)
            session.flush()  # Get sale ID
            
            # Add sale items and update stock
            for item in self.cart_items:
                # Create sale item
                sale_item = SaleItem(
                    sale_id=sale.id,
                    product_id=item['product_id'],
                    quantity=item['quantity'],
                    unit_price=item['price'],
                    total_price=item['total']
                )
                session.add(sale_item)
                
                # Update product stock
                product = session.query(Product).get(item['product_id'])
                product.stock_quantity -= item['quantity']
                
                # Record stock movement
                stock_movement = StockMovement(
                    product_id=item['product_id'],
                    movement_type="out",
                    quantity=item['quantity'],
                    reference_type="sale",
                    reference_id=sale.id,
                    notes=f"Sale #{sale.sale_number}",
                    created_by=current_user.username if current_user else "System"
                )
                session.add(stock_movement)
            
            session.commit()
            
            messagebox.showinfo("Sale Complete", 
                              f"Sale #{sale.sale_number} processed successfully!\n"
                              f"Total: {total_with_tax:,.0f} {DatabaseUtils.get_setting_value('currency', 'FCFA')}")
            
            # Print receipt (optional)
            if messagebox.askyesno("Print Receipt", "Would you like to print a receipt?"):
                self.print_receipt(sale)
            
            # Clear cart for new sale
            self.new_sale()
            self.refresh_products()
            self.update_dashboard()
            
        except Exception as e:
            session.rollback()
            messagebox.showerror("Sale Error", f"Failed to process sale: {e}")
        finally:
            session.close()
    
    def print_receipt(self, sale):
        """Print receipt for the sale"""
        try:
            from utils.receipt_printer import ReceiptPrinter
            printer = ReceiptPrinter()
            receipt_path = printer.generate_receipt(sale)
            messagebox.showinfo("Receipt", f"Receipt saved to:\n{receipt_path}")
        except Exception as e:
            messagebox.showerror("Print Error", f"Failed to print receipt: {e}")
    
    def hold_sale(self):
        """Hold current sale for later"""
        if not self.cart_items:
            messagebox.showwarning("Empty Cart", "No items to hold.")
            return
        
        # TODO: Implement sale holding functionality
        messagebox.showinfo("Hold Sale", "Sale holding feature coming soon!")
    
    def new_sale(self):
        """Start a new sale"""
        self.cart_items.clear()
        self.refresh_cart()
        self.calculate_totals()
        self.paid_var.set("")
        self.search_var.set("")

        # Reload customers to include new entries and reset selection
        self.load_customers()

        # Focus search box and refresh product list
        self.search_var.set("")
        self.refresh_products()
        self.update_dashboard()


    def destroy(self):
        if self.dashboard_job:
            try:
                self.parent.after_cancel(self.dashboard_job)
            except Exception:
                pass
            self.dashboard_job = None
        if self.inventory_binding:
            try:
                self.parent.unbind('<<InventoryChanged>>', self.inventory_binding)
            except Exception:
                pass

