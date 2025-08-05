# gui/inventory_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.database import db_manager
from database.models import Product, Category, StockMovement

class InventoryWindow:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup inventory management interface"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Products tab
        self.products_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.products_frame, text="Products")
        self.setup_products_tab()
        
        # Categories tab
        self.categories_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.categories_frame, text="Categories")
        self.setup_categories_tab()
        
        # Stock Movements tab
        self.movements_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.movements_frame, text="Stock Movements")
        self.setup_movements_tab()
        
        # Low Stock Alert tab
        self.alerts_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.alerts_frame, text="Low Stock Alerts")
        self.setup_alerts_tab()
    
    def setup_products_tab(self):
        """Setup products management tab"""
        # Control panel
        control_frame = ttk.Frame(self.products_frame)
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        control_frame.columnconfigure(2, weight=1)
        
        # Buttons
        ttk.Button(control_frame, text="Add Product", command=self.add_product).grid(row=0, column=0, padx=2)
        ttk.Button(control_frame, text="Edit Product", command=self.edit_product).grid(row=0, column=1, padx=2)
        ttk.Button(control_frame, text="Delete Product", command=self.delete_product).grid(row=0, column=2, padx=2)
        ttk.Button(control_frame, text="Adjust Stock", command=self.adjust_stock).grid(row=0, column=3, padx=2)
        ttk.Button(control_frame, text="Refresh", command=self.refresh_products).grid(row=0, column=4, padx=2)
        
        # Search
        ttk.Label(control_frame, text="Search:").grid(row=0, column=5, padx=(10, 2))
        self.product_search_var = tk.StringVar()
        self.product_search_var.trace('w', self.on_product_search)
        ttk.Entry(control_frame, textvariable=self.product_search_var, width=20).grid(row=0, column=6, padx=2)
        
        # Products treeview
        products_tree_frame = ttk.Frame(self.products_frame)
        products_tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        products_tree_frame.columnconfigure(0, weight=1)
        products_tree_frame.rowconfigure(0, weight=1)
        
        columns = ('ID', 'Name', 'Category', 'Barcode', 'Unit', 'Cost', 'Price', 'Stock', 'Min Stock', 'Status')
        self.products_tree = ttk.Treeview(products_tree_frame, columns=columns, show='headings', height=20)
        
        # Define headings and columns
        headings = {
            'ID': ('ID', 50, 'center'),
            'Name': ('Product Name', 200, 'w'),
            'Category': ('Category', 120, 'center'),
            'Barcode': ('Barcode', 100, 'center'),
            'Unit': ('Unit', 60, 'center'),
            'Cost': ('Cost Price', 100, 'e'),
            'Price': ('Selling Price', 100, 'e'),
            'Stock': ('Stock', 80, 'center'),
            'Min Stock': ('Min Stock', 80, 'center'),
            'Status': ('Status', 80, 'center')
        }
        
        for col, (text, width, anchor) in headings.items():
            self.products_tree.heading(col, text=text)
            self.products_tree.column(col, width=width, anchor=anchor)
        
        # Scrollbars
        products_v_scroll = ttk.Scrollbar(products_tree_frame, orient=tk.VERTICAL, command=self.products_tree.yview)
        products_h_scroll = ttk.Scrollbar(products_tree_frame, orient=tk.HORIZONTAL, command=self.products_tree.xview)
        self.products_tree.configure(yscrollcommand=products_v_scroll.set, xscrollcommand=products_h_scroll.set)
        
        self.products_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        products_v_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        products_h_scroll.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        self.products_frame.columnconfigure(0, weight=1)
        self.products_frame.rowconfigure(1, weight=1)
    
    def setup_categories_tab(self):
        """Setup categories management tab"""
        # Control panel
        cat_control_frame = ttk.Frame(self.categories_frame)
        cat_control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Button(cat_control_frame, text="Add Category", command=self.add_category).grid(row=0, column=0, padx=2)
        ttk.Button(cat_control_frame, text="Edit Category", command=self.edit_category).grid(row=0, column=1, padx=2)
        ttk.Button(cat_control_frame, text="Delete Category", command=self.delete_category).grid(row=0, column=2, padx=2)
        
        # Categories treeview
        categories_tree_frame = ttk.Frame(self.categories_frame)
        categories_tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        categories_tree_frame.columnconfigure(0, weight=1)
        categories_tree_frame.rowconfigure(0, weight=1)
        
        cat_columns = ('ID', 'Name', 'Description', 'Product Count', 'Created')
        self.categories_tree = ttk.Treeview(categories_tree_frame, columns=cat_columns, show='headings')
        
        # Define category headings
        cat_headings = {
            'ID': ('ID', 50, 'center'),
            'Name': ('Category Name', 200, 'w'),
            'Description': ('Description', 300, 'w'),
            'Product Count': ('Products', 100, 'center'),
            'Created': ('Created Date', 150, 'center')
        }
        
        for col, (text, width, anchor) in cat_headings.items():
            self.categories_tree.heading(col, text=text)
            self.categories_tree.column(col, width=width, anchor=anchor)
        
        # Category scrollbar
        cat_v_scroll = ttk.Scrollbar(categories_tree_frame, orient=tk.VERTICAL, command=self.categories_tree.yview)
        self.categories_tree.configure(yscrollcommand=cat_v_scroll.set)
        
        self.categories_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        cat_v_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights
        self.categories_frame.columnconfigure(0, weight=1)
        self.categories_frame.rowconfigure(1, weight=1)
    
    def setup_movements_tab(self):
        """Setup stock movements tab"""
        # Control panel
        mov_control_frame = ttk.Frame(self.movements_frame)
        mov_control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        mov_control_frame.columnconfigure(3, weight=1)
        
        ttk.Button(mov_control_frame, text="Add Stock", command=self.add_stock).grid(row=0, column=0, padx=2)
        ttk.Button(mov_control_frame, text="Remove Stock", command=self.remove_stock).grid(row=0, column=1, padx=2)
        ttk.Button(mov_control_frame, text="Refresh", command=self.refresh_movements).grid(row=0, column=2, padx=2)
        
        # Filter by movement type
        ttk.Label(mov_control_frame, text="Filter:").grid(row=0, column=4, padx=(10, 2))
        self.movement_filter_var = tk.StringVar(value="All")
        movement_filter = ttk.Combobox(mov_control_frame, textvariable=self.movement_filter_var, 
                                     values=["All", "in", "out", "adjustment"], state="readonly", width=15)
        movement_filter.grid(row=0, column=5, padx=2)
        movement_filter.bind('<<ComboboxSelected>>', self.on_movement_filter_change)
        
        # Movements treeview
        movements_tree_frame = ttk.Frame(self.movements_frame)
        movements_tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        movements_tree_frame.columnconfigure(0, weight=1)
        movements_tree_frame.rowconfigure(0, weight=1)
        
        mov_columns = ('ID', 'Product', 'Type', 'Quantity', 'Reference', 'Notes', 'Date', 'User')
        self.movements_tree = ttk.Treeview(movements_tree_frame, columns=mov_columns, show='headings')
        
        # Define movement headings
        mov_headings = {
            'ID': ('ID', 50, 'center'),
            'Product': ('Product', 200, 'w'),
            'Type': ('Type', 80, 'center'),
            'Quantity': ('Quantity', 100, 'center'),
            'Reference': ('Reference', 120, 'center'),
            'Notes': ('Notes', 200, 'w'),
            'Date': ('Date', 150, 'center'),
            'User': ('User', 100, 'center')
        }
        
        for col, (text, width, anchor) in mov_headings.items():
            self.movements_tree.heading(col, text=text)
            self.movements_tree.column(col, width=width, anchor=anchor)
        
        # Movement scrollbars
        mov_v_scroll = ttk.Scrollbar(movements_tree_frame, orient=tk.VERTICAL, command=self.movements_tree.yview)
        mov_h_scroll = ttk.Scrollbar(movements_tree_frame, orient=tk.HORIZONTAL, command=self.movements_tree.xview)
        self.movements_tree.configure(yscrollcommand=mov_v_scroll.set, xscrollcommand=mov_h_scroll.set)
        
        self.movements_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        mov_v_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        mov_h_scroll.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        self.movements_frame.columnconfigure(0, weight=1)
        self.movements_frame.rowconfigure(1, weight=1)
    
    def setup_alerts_tab(self):
        """Setup low stock alerts tab"""
        # Alert info
        alert_info_frame = ttk.Frame(self.alerts_frame)
        alert_info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(alert_info_frame, text="Products below minimum stock level:", 
                 font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky=tk.W)
        
        ttk.Button(alert_info_frame, text="Refresh Alerts", command=self.refresh_alerts).grid(row=0, column=1, padx=10)
        
        # Low stock treeview
        alerts_tree_frame = ttk.Frame(self.alerts_frame)
        alerts_tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        alerts_tree_frame.columnconfigure(0, weight=1)
        alerts_tree_frame.rowconfigure(0, weight=1)
        
        alert_columns = ('ID', 'Product', 'Category', 'Current Stock', 'Min Stock', 'Shortage', 'Status')
        self.alerts_tree = ttk.Treeview(alerts_tree_frame, columns=alert_columns, show='headings')
        
        # Define alert headings
        alert_headings = {
            'ID': ('ID', 50, 'center'),
            'Product': ('Product Name', 250, 'w'),
            'Category': ('Category', 120, 'center'),
            'Current Stock': ('Current Stock', 100, 'center'),
            'Min Stock': ('Min Stock', 100, 'center'),
            'Shortage': ('Shortage', 100, 'center'),
            'Status': ('Status', 100, 'center')
        }
        
        for col, (text, width, anchor) in alert_headings.items():
            self.alerts_tree.heading(col, text=text)
            self.alerts_tree.column(col, width=width, anchor=anchor)
        
        # Alert scrollbar
        alert_v_scroll = ttk.Scrollbar(alerts_tree_frame, orient=tk.VERTICAL, command=self.alerts_tree.yview)
        self.alerts_tree.configure(yscrollcommand=alert_v_scroll.set)
        
        self.alerts_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        alert_v_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights
        self.alerts_frame.columnconfigure(0, weight=1)
        self.alerts_frame.rowconfigure(1, weight=1)
    
    def load_data(self):
        """Load all data"""
        self.refresh_products()
        self.refresh_categories()
        self.refresh_movements()
        self.refresh_alerts()
    
    def refresh_products(self, search_term=""):
        """Refresh products list"""
        session = db_manager.get_session()
        try:
            # Clear existing items
            for item in self.products_tree.get_children():
                self.products_tree.delete(item)
            
            # Build query
            query = session.query(Product)
            
            if search_term:
                query = query.filter(
                    Product.name.contains(search_term) | 
                    Product.barcode.contains(search_term)
                )
            
            products = query.order_by(Product.name).all()
            
            # Populate treeview
            for product in products:
                category_name = product.category.name if product.category else "N/A"
                status = "Active" if product.is_active else "Inactive"
                
                values = (
                    product.id,
                    product.name,
                    category_name,
                    product.barcode or "",
                    product.unit,
                    f"{product.cost_price:,.0f}",
                    f"{product.selling_price:,.0f}",
                    product.stock_quantity,
                    product.min_stock_level,
                    status
                )
                
                item_id = self.products_tree.insert('', tk.END, values=values)
                
                # Highlight low stock items
                if product.stock_quantity <= product.min_stock_level:
                    self.products_tree.item(item_id, tags=('low_stock',))
            
            # Configure tags
            self.products_tree.tag_configure('low_stock', background='#ffeeee', foreground='red')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh products: {e}")
        finally:
            session.close()
    
    def refresh_categories(self):
        """Refresh categories list"""
        session = db_manager.get_session()
        try:
            # Clear existing items
            for item in self.categories_tree.get_children():
                self.categories_tree.delete(item)
            
            categories = session.query(Category).order_by(Category.name).all()
            
            for category in categories:
                # Count products in category
                product_count = len(category.products)
                
                values = (
                    category.id,
                    category.name,
                    category.description or "",
                    product_count,
                    category.created_at.strftime("%Y-%m-%d") if category.created_at else ""
                )
                self.categories_tree.insert('', tk.END, values=values)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh categories: {e}")
        finally:
            session.close()
    
    def refresh_movements(self, filter_type="All"):
        """Refresh stock movements list"""
        session = db_manager.get_session()
        try:
            # Clear existing items
            for item in self.movements_tree.get_children():
                self.movements_tree.delete(item)
            
            # Build query
            query = session.query(StockMovement)
            
            if filter_type != "All":
                query = query.filter(StockMovement.movement_type == filter_type)
            
            movements = query.order_by(StockMovement.created_at.desc()).limit(1000).all()
            
            for movement in movements:
                product_name = movement.product.name if movement.product else "Unknown"
                
                values = (
                    movement.id,
                    product_name,
                    movement.movement_type.title(),
                    f"{movement.quantity:,.1f}",
                    f"{movement.reference_type or ''} #{movement.reference_id or ''}",
                    movement.notes or "",
                    movement.created_at.strftime("%Y-%m-%d %H:%M") if movement.created_at else "",
                    movement.created_by or ""
                )
                
                item_id = self.movements_tree.insert('', tk.END, values=values)
                
                # Color code by movement type
                if movement.movement_type == "in":
                    self.movements_tree.item(item_id, tags=('stock_in',))
                elif movement.movement_type == "out":
                    self.movements_tree.item(item_id, tags=('stock_out',))
            
            # Configure tags
            self.movements_tree.tag_configure('stock_in', background='#eeffee')
            self.movements_tree.tag_configure('stock_out', background='#ffeeee')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh movements: {e}")
        finally:
            session.close()
    
    def refresh_alerts(self):
        """Refresh low stock alerts"""
        session = db_manager.get_session()
        try:
            # Clear existing items
            for item in self.alerts_tree.get_children():
                self.alerts_tree.delete(item)
            
            # Find products below minimum stock
            products = session.query(Product).filter(
                Product.is_active == True,
                Product.stock_quantity <= Product.min_stock_level
            ).order_by(Product.stock_quantity).all()
            
            for product in products:
                category_name = product.category.name if product.category else "N/A"
                shortage = product.min_stock_level - product.stock_quantity
                
                if product.stock_quantity <= 0:
                    status = "Out of Stock"
                elif product.stock_quantity <= product.min_stock_level * 0.5:
                    status = "Critical"
                else:
                    status = "Low Stock"
                
                values = (
                    product.id,
                    product.name,
                    category_name,
                    product.stock_quantity,
                    product.min_stock_level,
                    shortage,
                    status
                )
                
                item_id = self.alerts_tree.insert('', tk.END, values=values)
                
                # Color code by severity
                if status == "Out of Stock":
                    self.alerts_tree.item(item_id, tags=('out_of_stock',))
                elif status == "Critical":
                    self.alerts_tree.item(item_id, tags=('critical',))
                else:
                    self.alerts_tree.item(item_id, tags=('low_stock',))
            
            # Configure tags
            self.alerts_tree.tag_configure('out_of_stock', background='#ff6666', foreground='white')
            self.alerts_tree.tag_configure('critical', background='#ffaaaa')
            self.alerts_tree.tag_configure('low_stock', background='#ffffaa')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh alerts: {e}")
        finally:
            session.close()
    
    # Event handlers
    def on_product_search(self, *args):
        """Handle product search"""
        search_term = self.product_search_var.get()
        self.refresh_products(search_term)
    
    def on_movement_filter_change(self, event):
        """Handle movement filter change"""
        filter_type = self.movement_filter_var.get()
        self.refresh_movements(filter_type)
    
    # Product management methods
    def add_product(self):
        """Add new product"""
        dialog = ProductDialog(self.parent, "Add Product")
        if dialog.result:
            session = db_manager.get_session()
            try:
                product = Product(**dialog.result)
                session.add(product)
                session.commit()
                messagebox.showinfo("Success", "Product added successfully!")
                self.refresh_products()
                self.refresh_alerts()
            except Exception as e:
                session.rollback()
                messagebox.showerror("Error", f"Failed to add product: {e}")
            finally:
                session.close()
    
    def edit_product(self):
        """Edit selected product"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a product to edit.")
            return
        
        product_id = self.products_tree.item(selection[0])['values'][0]
        
        session = db_manager.get_session()
        try:
            product = session.query(Product).get(product_id)
            if not product:
                messagebox.showerror("Error", "Product not found.")
                return
            
            dialog = ProductDialog(self.parent, "Edit Product", product)
            if dialog.result:
                for key, value in dialog.result.items():
                    setattr(product, key, value)
                
                session.commit()
                messagebox.showinfo("Success", "Product updated successfully!")
                self.refresh_products()
                self.refresh_alerts()
                
        except Exception as e:
            session.rollback()
            messagebox.showerror("Error", f"Failed to edit product: {e}")
        finally:
            session.close()
    
    def delete_product(self):
        """Delete selected product"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a product to delete.")
            return
        
        product_name = self.products_tree.item(selection[0])['values'][1]
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{product_name}'?"):
            return
        
        product_id = self.products_tree.item(selection[0])['values'][0]
        
        session = db_manager.get_session()
        try:
            product = session.query(Product).get(product_id)
            if product:
                # Instead of deleting, mark as inactive
                product.is_active = False
                session.commit()
                messagebox.showinfo("Success", "Product deactivated successfully!")
                self.refresh_products()
                
        except Exception as e:
            session.rollback()
            messagebox.showerror("Error", f"Failed to delete product: {e}")
        finally:
            session.close()
    
    def adjust_stock(self):
        """Adjust stock for selected product"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a product to adjust stock.")
            return
        
        product_id = self.products_tree.item(selection[0])['values'][0]
        product_name = self.products_tree.item(selection[0])['values'][1]
        current_stock = int(self.products_tree.item(selection[0])['values'][7])
        
        dialog = StockAdjustmentDialog(self.parent, product_name, current_stock)
        if dialog.result:
            session = db_manager.get_session()
            try:
                product = session.query(Product).get(product_id)
                if product:
                    old_stock = product.stock_quantity
                    new_stock = dialog.result['new_quantity']
                    adjustment = new_stock - old_stock
                    
                    # Update product stock
                    product.stock_quantity = new_stock
                    
                    # Record stock movement
                    movement = StockMovement(
                        product_id=product_id,
                        movement_type="adjustment",
                        quantity=abs(adjustment),
                        reference_type="adjustment",
                        notes=f"Stock adjustment: {old_stock} → {new_stock}. Reason: {dialog.result['reason']}",
                        created_by="System"
                    )
                    session.add(movement)
                    
                    session.commit()
                    messagebox.showinfo("Success", "Stock adjusted successfully!")
                    self.refresh_products()
                    self.refresh_movements()
                    self.refresh_alerts()
                    
            except Exception as e:
                session.rollback()
                messagebox.showerror("Error", f"Failed to adjust stock: {e}")
            finally:
                session.close()
    
    # Category management methods
    def add_category(self):
        """Add new category"""
        dialog = CategoryDialog(self.parent, "Add Category")
        if dialog.result:
            session = db_manager.get_session()
            try:
                category = Category(**dialog.result)
                session.add(category)
                session.commit()
                messagebox.showinfo("Success", "Category added successfully!")
                self.refresh_categories()
            except Exception as e:
                session.rollback()
                messagebox.showerror("Error", f"Failed to add category: {e}")
            finally:
                session.close()
    
    def edit_category(self):
        """Edit selected category"""
        selection = self.categories_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a category to edit.")
            return
        
        category_id = self.categories_tree.item(selection[0])['values'][0]
        
        session = db_manager.get_session()
        try:
            category = session.query(Category).get(category_id)
            if not category:
                messagebox.showerror("Error", "Category not found.")
                return
            
            dialog = CategoryDialog(self.parent, "Edit Category", category)
            if dialog.result:
                for key, value in dialog.result.items():
                    setattr(category, key, value)
                
                session.commit()
                messagebox.showinfo("Success", "Category updated successfully!")
                self.refresh_categories()
                
        except Exception as e:
            session.rollback()
            messagebox.showerror("Error", f"Failed to edit category: {e}")
        finally:
            session.close()
    
    def delete_category(self):
        """Delete selected category"""
        selection = self.categories_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a category to delete.")
            return
        
        category_name = self.categories_tree.item(selection[0])['values'][1]
        product_count = int(self.categories_tree.item(selection[0])['values'][3])
        
        if product_count > 0:
            messagebox.showwarning("Cannot Delete", 
                                 f"Category '{category_name}' has {product_count} products. "
                                 "Please move or delete products first.")
            return
        
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete category '{category_name}'?"):
            return
        
        category_id = self.categories_tree.item(selection[0])['values'][0]
        
        session = db_manager.get_session()
        try:
            category = session.query(Category).get(category_id)
            if category:
                session.delete(category)
                session.commit()
                messagebox.showinfo("Success", "Category deleted successfully!")
                self.refresh_categories()
                
        except Exception as e:
            session.rollback()
            messagebox.showerror("Error", f"Failed to delete category: {e}")
        finally:
            session.close()
    
    # Stock movement methods
    def add_stock(self):
        """Add stock to a product"""
        dialog = StockMovementDialog(self.parent, "Add Stock", "in")
        if dialog.result:
            self.process_stock_movement(dialog.result)
    
    def remove_stock(self):
        """Remove stock from a product"""
        dialog = StockMovementDialog(self.parent, "Remove Stock", "out")
        if dialog.result:
            self.process_stock_movement(dialog.result)
    
    def process_stock_movement(self, movement_data):
        """Process stock movement"""
        session = db_manager.get_session()
        try:
            product = session.query(Product).get(movement_data['product_id'])
            if not product:
                messagebox.showerror("Error", "Product not found.")
                return
            
            # Update product stock
            if movement_data['movement_type'] == "in":
                product.stock_quantity += movement_data['quantity']
            else:
                if product.stock_quantity < movement_data['quantity']:
                    if not messagebox.askyesno("Insufficient Stock", 
                                             f"Only {product.stock_quantity} units available. Continue anyway?"):
                        return
                product.stock_quantity -= movement_data['quantity']
                product.stock_quantity = max(0, product.stock_quantity)  # Prevent negative stock
            
            # Record stock movement
            movement = StockMovement(
                product_id=movement_data['product_id'],
                movement_type=movement_data['movement_type'],
                quantity=movement_data['quantity'],
                reference_type="manual",
                notes=movement_data['notes'],
                created_by="System"
            )
            session.add(movement)
            
            session.commit()
            messagebox.showinfo("Success", "Stock movement processed successfully!")
            self.refresh_products()
            self.refresh_movements()
            self.refresh_alerts()
            
        except Exception as e:
            session.rollback()
            messagebox.showerror("Error", f"Failed to process stock movement: {e}")
        finally:
            session.close()


# Dialog classes for product and category management
class ProductDialog:
    def __init__(self, parent, title, product=None):
        self.result = None
        self.product = product
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.geometry("500x600+{}+{}".format(
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        self.setup_ui()
        self.load_categories()
        
        if product:
            self.load_product_data()
    
    def setup_ui(self):
        """Setup product dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Product name
        ttk.Label(main_frame, text="Product Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=40).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Description
        ttk.Label(main_frame, text="Description:").grid(row=1, column=0, sticky=(tk.W, tk.N), pady=5)
        self.description_text = tk.Text(main_frame, width=40, height=3)
        self.description_text.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Barcode
        ttk.Label(main_frame, text="Barcode:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.barcode_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.barcode_var, width=40).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Category
        ttk.Label(main_frame, text="Category:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(main_frame, textvariable=self.category_var, width=37, state="readonly")
        self.category_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Unit
        ttk.Label(main_frame, text="Unit:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.unit_var = tk.StringVar(value="piece")
        unit_combo = ttk.Combobox(main_frame, textvariable=self.unit_var, 
                                values=["piece", "bag", "meter", "kg", "ton", "liter", "box", "set"], 
                                width=37, state="readonly")
        unit_combo.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Cost price
        ttk.Label(main_frame, text="Cost Price:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.cost_var = tk.StringVar(value="0")
        ttk.Entry(main_frame, textvariable=self.cost_var, width=40).grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Selling price
        ttk.Label(main_frame, text="Selling Price:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.price_var = tk.StringVar(value="0")
        ttk.Entry(main_frame, textvariable=self.price_var, width=40).grid(row=6, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Stock quantity
        ttk.Label(main_frame, text="Stock Quantity:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.stock_var = tk.StringVar(value="0")
        ttk.Entry(main_frame, textvariable=self.stock_var, width=40).grid(row=7, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Minimum stock level
        ttk.Label(main_frame, text="Min Stock Level:").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.min_stock_var = tk.StringVar(value="5")
        ttk.Entry(main_frame, textvariable=self.min_stock_var, width=40).grid(row=8, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Active status
        self.active_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="Active", variable=self.active_var).grid(row=9, column=1, sticky=tk.W, pady=10)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=10, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
    
    def load_categories(self):
        """Load categories for dropdown"""
        session = db_manager.get_session()
        try:
            categories = session.query(Category).order_by(Category.name).all()
            category_names = [cat.name for cat in categories]
            self.category_combo['values'] = category_names
            if category_names:
                self.category_combo.set(category_names[0])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load categories: {e}")
        finally:
            session.close()
    
    def load_product_data(self):
        """Load existing product data"""
        if self.product:
            self.name_var.set(self.product.name)
            self.description_text.insert('1.0', self.product.description or "")
            self.barcode_var.set(self.product.barcode or "")
            if self.product.category:
                self.category_var.set(self.product.category.name)
            self.unit_var.set(self.product.unit)
            self.cost_var.set(str(self.product.cost_price))
            self.price_var.set(str(self.product.selling_price))
            self.stock_var.set(str(self.product.stock_quantity))
            self.min_stock_var.set(str(self.product.min_stock_level))
            self.active_var.set(self.product.is_active)
    
    def save_product(self):
        """Save product data"""
        try:
            # Validate required fields
            if not self.name_var.get().strip():
                messagebox.showwarning("Validation Error", "Product name is required.")
                return
            
            if not self.category_var.get():
                messagebox.showwarning("Validation Error", "Please select a category.")
                return
            
            # Get category ID
            session = db_manager.get_session()
            try:
                category = session.query(Category).filter(Category.name == self.category_var.get()).first()
                if not category:
                    messagebox.showerror("Error", "Selected category not found.")
                    return
                
                category_id = category.id
            finally:
                session.close()
            
            # Prepare data
            self.result = {
                'name': self.name_var.get().strip(),
                'description': self.description_text.get('1.0', tk.END).strip(),
                'barcode': self.barcode_var.get().strip() or None,
                'category_id': category_id,
                'unit': self.unit_var.get(),
                'cost_price': float(self.cost_var.get() or 0),
                'selling_price': float(self.price_var.get() or 0),
                'stock_quantity': int(self.stock_var.get() or 0),
                'min_stock_level': int(self.min_stock_var.get() or 0),
                'is_active': self.active_var.get()
            }
            
            self.dialog.destroy()
            
        except ValueError as e:
            messagebox.showerror("Validation Error", "Please enter valid numeric values for prices and quantities.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save product: {e}")


class CategoryDialog:
    def __init__(self, parent, title, category=None):
        self.result = None
        self.category = category
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.geometry("400x300+{}+{}".format(
            parent.winfo_rootx() + 100,
            parent.winfo_rooty() + 100
        ))
        
        self.setup_ui()
        
        if category:
            self.load_category_data()
    
    def setup_ui(self):
        """Setup category dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Category name
        ttk.Label(main_frame, text="Category Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=40).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Description
        ttk.Label(main_frame, text="Description:").grid(row=1, column=0, sticky=(tk.W, tk.N), pady=5)
        self.description_text = tk.Text(main_frame, width=40, height=8)
        self.description_text.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save_category).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
    
    def load_category_data(self):
        """Load existing category data"""
        if self.category:
            self.name_var.set(self.category.name)
            self.description_text.insert('1.0', self.category.description or "")
    
    def save_category(self):
        """Save category data"""
        try:
            # Validate required fields
            if not self.name_var.get().strip():
                messagebox.showwarning("Validation Error", "Category name is required.")
                return
            
            # Prepare data
            self.result = {
                'name': self.name_var.get().strip(),
                'description': self.description_text.get('1.0', tk.END).strip()
            }
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save category: {e}")


class StockAdjustmentDialog:
    def __init__(self, parent, product_name, current_stock):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Stock Adjustment")
        self.dialog.geometry("400x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.geometry("400x250+{}+{}".format(
            parent.winfo_rootx() + 100,
            parent.winfo_rooty() + 100
        ))
        
        self.setup_ui(product_name, current_stock)
    
    def setup_ui(self, product_name, current_stock):
        """Setup stock adjustment dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Product info
        ttk.Label(main_frame, text=f"Product: {product_name}", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(main_frame, text=f"Current Stock: {current_stock}").grid(row=1, column=0, columnspan=2, pady=5)
        
        # New quantity
        ttk.Label(main_frame, text="New Quantity:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.quantity_var = tk.StringVar(value=str(current_stock))
        ttk.Entry(main_frame, textvariable=self.quantity_var, width=20).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Reason
        ttk.Label(main_frame, text="Reason:").grid(row=3, column=0, sticky=(tk.W, tk.N), pady=5)
        self.reason_text = tk.Text(main_frame, width=30, height=4)
        self.reason_text.grid(row=3, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save_adjustment).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
    
    def save_adjustment(self):
        """Save stock adjustment"""
        try:
            new_quantity = int(self.quantity_var.get())
            reason = self.reason_text.get('1.0', tk.END).strip()
            
            if new_quantity < 0:
                messagebox.showwarning("Invalid Quantity", "Quantity cannot be negative.")
                return
            
            if not reason:
                messagebox.showwarning("Missing Reason", "Please provide a reason for the adjustment.")
                return
            
            self.result = {
                'new_quantity': new_quantity,
                'reason': reason
            }
            
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid quantity.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save adjustment: {e}")


class StockMovementDialog:
    def __init__(self, parent, title, movement_type):
        self.result = None
        self.movement_type = movement_type
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.geometry("400x300+{}+{}".format(
            parent.winfo_rootx() + 100,
            parent.winfo_rooty() + 100
        ))
        
        self.setup_ui()
        self.load_products()
    
    def setup_ui(self):
        """Setup stock movement dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Product selection
        ttk.Label(main_frame, text="Product:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.product_var = tk.StringVar()
        self.product_combo = ttk.Combobox(main_frame, textvariable=self.product_var, width=37, state="readonly")
        self.product_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Quantity
        ttk.Label(main_frame, text="Quantity:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.quantity_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.quantity_var, width=40).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Notes
        ttk.Label(main_frame, text="Notes:").grid(row=2, column=0, sticky=(tk.W, tk.N), pady=5)
        self.notes_text = tk.Text(main_frame, width=40, height=6)
        self.notes_text.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save_movement).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
    
    def load_products(self):
        """Load products for dropdown"""
        session = db_manager.get_session()
        try:
            products = session.query(Product).filter(Product.is_active == True).order_by(Product.name).all()
            self.products = products  # Store for later reference
            product_names = [f"{p.id} - {p.name}" for p in products]
            self.product_combo['values'] = product_names
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load products: {e}")
        finally:
            session.close()
    
    def save_movement(self):
        """Save stock movement"""
        try:
            if not self.product_var.get():
                messagebox.showwarning("Missing Product", "Please select a product.")
                return
            
            product_id = int(self.product_var.get().split(' - ')[0])
            quantity = float(self.quantity_var.get())
            notes = self.notes_text.get('1.0', tk.END).strip()
            
            if quantity <= 0:
                messagebox.showwarning("Invalid Quantity", "Quantity must be greater than 0.")
                return
            
            self.result = {
                'product_id': product_id,
                'movement_type': self.movement_type,
                'quantity': quantity,
                'notes': notes
            }
            
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid quantity.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save movement: {e}")