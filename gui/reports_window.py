# gui/reports_window.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date, timedelta
from database.database import db_manager, DatabaseUtils
from database.models import Sale, Product, SaleItem, Category, StockMovement
import csv
import os

class ReportsWindow:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        
    def setup_ui(self):
        """Setup reports interface"""
        # Create notebook for different report types
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Sales Reports tab
        self.sales_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sales_frame, text="Sales Reports")
        self.setup_sales_reports()
        
        # Inventory Reports tab
        self.inventory_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.inventory_frame, text="Inventory Reports")
        self.setup_inventory_reports()
        
        # Product Performance tab
        self.performance_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.performance_frame, text="Product Performance")
        self.setup_performance_reports()
        
        # Financial Summary tab
        self.financial_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.financial_frame, text="Financial Summary")
        self.setup_financial_reports()
    
    def setup_sales_reports(self):
        """Setup sales reports tab"""
        # Control panel
        control_frame = ttk.LabelFrame(self.sales_frame, text="Sales Report Options", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        control_frame.columnconfigure(3, weight=1)
        
        # Date range selection
        ttk.Label(control_frame, text="From Date:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.from_date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        from_date_entry = ttk.Entry(control_frame, textvariable=self.from_date_var, width=12)
        from_date_entry.grid(row=0, column=1, padx=5)

        ttk.Label(control_frame, text="To Date:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        self.to_date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        to_date_entry = ttk.Entry(control_frame, textvariable=self.to_date_var, width=12)
        to_date_entry.grid(row=0, column=3, padx=5)

        # Time range selection
        ttk.Label(control_frame, text="From Time:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        self.from_time_var = tk.StringVar(value="00:00")
        ttk.Entry(control_frame, textvariable=self.from_time_var, width=10).grid(row=1, column=1, padx=5)

        ttk.Label(control_frame, text="To Time:").grid(row=1, column=2, sticky=tk.W, padx=(10, 5))
        self.to_time_var = tk.StringVar(value="23:59")
        ttk.Entry(control_frame, textvariable=self.to_time_var, width=10).grid(row=1, column=3, padx=5)

        # Quick date buttons
        quick_dates_frame = ttk.Frame(control_frame)
        quick_dates_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        ttk.Button(quick_dates_frame, text="Today", command=self.set_today).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_dates_frame, text="Yesterday", command=self.set_yesterday).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_dates_frame, text="This Week", command=self.set_this_week).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_dates_frame, text="This Month", command=self.set_this_month).pack(side=tk.LEFT, padx=2)
        
        # Action buttons
        actions_frame = ttk.Frame(control_frame)
        actions_frame.grid(row=3, column=0, columnspan=4, pady=10)
        
        ttk.Button(actions_frame, text="Generate Report", command=self.generate_sales_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Export to CSV", command=self.export_sales_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Print Report", command=self.print_sales_report).pack(side=tk.LEFT, padx=5)
        
        # Results area
        results_frame = ttk.LabelFrame(self.sales_frame, text="Sales Report Results", padding="5")
        results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        
        # Summary labels
        self.sales_summary_frame = ttk.Frame(results_frame)
        self.sales_summary_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Sales data treeview
        sales_columns = ('Date', 'Receipt #', 'Customer', 'Items', 'Subtotal', 'Tax', 'Total', 'Payment')
        self.sales_tree = ttk.Treeview(results_frame, columns=sales_columns, show='headings', height=15)
        
        for col in sales_columns:
            self.sales_tree.heading(col, text=col)
        
        # Configure column widths
        self.sales_tree.column('Date', width=100, anchor='center')
        self.sales_tree.column('Receipt #', width=120, anchor='center')
        self.sales_tree.column('Customer', width=150, anchor='w')
        self.sales_tree.column('Items', width=60, anchor='center')
        self.sales_tree.column('Subtotal', width=100, anchor='e')
        self.sales_tree.column('Tax', width=80, anchor='e')
        self.sales_tree.column('Total', width=100, anchor='e')
        self.sales_tree.column('Payment', width=80, anchor='center')
        
        # Scrollbars
        sales_v_scroll = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.sales_tree.yview)
        sales_h_scroll = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.sales_tree.xview)
        self.sales_tree.configure(yscrollcommand=sales_v_scroll.set, xscrollcommand=sales_h_scroll.set)
        
        self.sales_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        sales_v_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
        sales_h_scroll.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        self.sales_frame.columnconfigure(0, weight=1)
        self.sales_frame.rowconfigure(1, weight=1)
    
    def setup_inventory_reports(self):
        """Setup inventory reports tab"""
        # Control panel
        inv_control_frame = ttk.LabelFrame(self.inventory_frame, text="Inventory Report Options", padding="10")
        inv_control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Report type selection
        ttk.Label(inv_control_frame, text="Report Type:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.inv_report_type = tk.StringVar(value="Current Stock")
        report_combo = ttk.Combobox(inv_control_frame, textvariable=self.inv_report_type, 
                                   values=["Current Stock", "Low Stock Items", "Stock Valuation", "Out of Stock"], 
                                   state="readonly", width=20)
        report_combo.grid(row=0, column=1, padx=5)
        
        # Category filter
        ttk.Label(inv_control_frame, text="Category:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        self.inv_category_var = tk.StringVar(value="All Categories")
        self.inv_category_combo = ttk.Combobox(inv_control_frame, textvariable=self.inv_category_var, 
                                             state="readonly", width=20)
        self.inv_category_combo.grid(row=0, column=3, padx=5)
        
        # Action buttons
        inv_actions_frame = ttk.Frame(inv_control_frame)
        inv_actions_frame.grid(row=1, column=0, columnspan=4, pady=10)
        
        ttk.Button(inv_actions_frame, text="Generate Report", command=self.generate_inventory_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(inv_actions_frame, text="Export to CSV", command=self.export_inventory_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(inv_actions_frame, text="Print Report", command=self.print_inventory_report).pack(side=tk.LEFT, padx=5)
        
        # Results area
        inv_results_frame = ttk.LabelFrame(self.inventory_frame, text="Inventory Report Results", padding="5")
        inv_results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        inv_results_frame.columnconfigure(0, weight=1)
        inv_results_frame.rowconfigure(1, weight=1)
        
        # Summary labels
        self.inv_summary_frame = ttk.Frame(inv_results_frame)
        self.inv_summary_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Inventory data treeview
        inv_columns = ('ID', 'Product', 'Category', 'Unit', 'Stock', 'Min Stock', 'Cost Price', 'Selling Price', 'Value')
        self.inventory_tree = ttk.Treeview(inv_results_frame, columns=inv_columns, show='headings', height=15)
        
        for col in inv_columns:
            self.inventory_tree.heading(col, text=col)
        
        # Configure column widths
        self.inventory_tree.column('ID', width=50, anchor='center')
        self.inventory_tree.column('Product', width=200, anchor='w')
        self.inventory_tree.column('Category', width=120, anchor='center')
        self.inventory_tree.column('Unit', width=60, anchor='center')
        self.inventory_tree.column('Stock', width=80, anchor='center')
        self.inventory_tree.column('Min Stock', width=80, anchor='center')
        self.inventory_tree.column('Cost Price', width=100, anchor='e')
        self.inventory_tree.column('Selling Price', width=100, anchor='e')
        self.inventory_tree.column('Value', width=120, anchor='e')
        
        # Scrollbars
        inv_v_scroll = ttk.Scrollbar(inv_results_frame, orient=tk.VERTICAL, command=self.inventory_tree.yview)
        inv_h_scroll = ttk.Scrollbar(inv_results_frame, orient=tk.HORIZONTAL, command=self.inventory_tree.xview)
        self.inventory_tree.configure(yscrollcommand=inv_v_scroll.set, xscrollcommand=inv_h_scroll.set)
        
        self.inventory_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        inv_v_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
        inv_h_scroll.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        # Load categories
        self.load_categories()
        
        # Configure grid weights
        self.inventory_frame.columnconfigure(0, weight=1)
        self.inventory_frame.rowconfigure(1, weight=1)
    
    def setup_performance_reports(self):
        """Setup product performance reports tab"""
        # Control panel
        perf_control_frame = ttk.LabelFrame(self.performance_frame, text="Performance Report Options", padding="10")
        perf_control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Date range
        ttk.Label(perf_control_frame, text="From Date:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.perf_from_date = tk.StringVar(value=(date.today() - timedelta(days=30)).strftime("%Y-%m-%d"))
        ttk.Entry(perf_control_frame, textvariable=self.perf_from_date, width=12).grid(row=0, column=1, padx=5)
        
        ttk.Label(perf_control_frame, text="To Date:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        self.perf_to_date = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        ttk.Entry(perf_control_frame, textvariable=self.perf_to_date, width=12).grid(row=0, column=3, padx=5)
        
        # Sort by
        ttk.Label(perf_control_frame, text="Sort by:").grid(row=0, column=4, sticky=tk.W, padx=(10, 5))
        self.perf_sort_var = tk.StringVar(value="Quantity Sold")
        sort_combo = ttk.Combobox(perf_control_frame, textvariable=self.perf_sort_var, 
                                 values=["Quantity Sold", "Revenue", "Profit", "Times Sold"], 
                                 state="readonly", width=15)
        sort_combo.grid(row=0, column=5, padx=5)
        
        # Action buttons
        perf_actions_frame = ttk.Frame(perf_control_frame)
        perf_actions_frame.grid(row=1, column=0, columnspan=6, pady=10)
        
        ttk.Button(perf_actions_frame, text="Generate Report", command=self.generate_performance_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(perf_actions_frame, text="Export to CSV", command=self.export_performance_csv).pack(side=tk.LEFT, padx=5)
        
        # Results area
        perf_results_frame = ttk.LabelFrame(self.performance_frame, text="Product Performance Results", padding="5")
        perf_results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        perf_results_frame.columnconfigure(0, weight=1)
        perf_results_frame.rowconfigure(0, weight=1)
        
        # Performance data treeview
        perf_columns = ('Rank', 'Product', 'Category', 'Qty Sold', 'Times Sold', 'Revenue', 'Avg Price', 'Last Sold')
        self.performance_tree = ttk.Treeview(perf_results_frame, columns=perf_columns, show='headings', height=20)
        
        for col in perf_columns:
            self.performance_tree.heading(col, text=col)
        
        # Configure column widths
        self.performance_tree.column('Rank', width=50, anchor='center')
        self.performance_tree.column('Product', width=200, anchor='w')
        self.performance_tree.column('Category', width=120, anchor='center')
        self.performance_tree.column('Qty Sold', width=80, anchor='center')
        self.performance_tree.column('Times Sold', width=80, anchor='center')
        self.performance_tree.column('Revenue', width=120, anchor='e')
        self.performance_tree.column('Avg Price', width=100, anchor='e')
        self.performance_tree.column('Last Sold', width=100, anchor='center')
        
        # Scrollbars
        perf_v_scroll = ttk.Scrollbar(perf_results_frame, orient=tk.VERTICAL, command=self.performance_tree.yview)
        perf_h_scroll = ttk.Scrollbar(perf_results_frame, orient=tk.HORIZONTAL, command=self.performance_tree.xview)
        self.performance_tree.configure(yscrollcommand=perf_v_scroll.set, xscrollcommand=perf_h_scroll.set)
        
        self.performance_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        perf_v_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        perf_h_scroll.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        self.performance_frame.columnconfigure(0, weight=1)
        self.performance_frame.rowconfigure(1, weight=1)
    
    def setup_financial_reports(self):
        """Setup financial summary reports tab"""
        # Control panel
        fin_control_frame = ttk.LabelFrame(self.financial_frame, text="Financial Summary Options", padding="10")
        fin_control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Period selection
        ttk.Label(fin_control_frame, text="Period:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.fin_period_var = tk.StringVar(value="This Month")
        period_combo = ttk.Combobox(fin_control_frame, textvariable=self.fin_period_var, 
                                   values=["Today", "This Week", "This Month", "Last Month", "This Year", "Custom"], 
                                   state="readonly", width=15)
        period_combo.grid(row=0, column=1, padx=5)
        period_combo.bind('<<ComboboxSelected>>', self.on_period_change)
        
        # Custom date range (initially hidden)
        self.custom_date_frame = ttk.Frame(fin_control_frame)
        self.custom_date_frame.grid(row=0, column=2, columnspan=4, padx=10)
        
        ttk.Label(self.custom_date_frame, text="From:").grid(row=0, column=0, padx=(0, 5))
        self.fin_from_date = tk.StringVar(value=date.today().replace(day=1).strftime("%Y-%m-%d"))
        ttk.Entry(self.custom_date_frame, textvariable=self.fin_from_date, width=12).grid(row=0, column=1, padx=5)
        
        ttk.Label(self.custom_date_frame, text="To:").grid(row=0, column=2, padx=(10, 5))
        self.fin_to_date = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        ttk.Entry(self.custom_date_frame, textvariable=self.fin_to_date, width=12).grid(row=0, column=3, padx=5)
        
        # Initially hide custom date range
        self.custom_date_frame.grid_remove()
        
        # Action buttons
        fin_actions_frame = ttk.Frame(fin_control_frame)
        fin_actions_frame.grid(row=1, column=0, columnspan=6, pady=10)
        
        ttk.Button(fin_actions_frame, text="Generate Summary", command=self.generate_financial_summary).pack(side=tk.LEFT, padx=5)
        ttk.Button(fin_actions_frame, text="Export Summary", command=self.export_financial_csv).pack(side=tk.LEFT, padx=5)
        
        # Results area
        fin_results_frame = ttk.LabelFrame(self.financial_frame, text="Financial Summary", padding="10")
        fin_results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        fin_results_frame.columnconfigure(1, weight=1)
        
        # Summary metrics
        self.create_financial_summary_ui(fin_results_frame)
        
        # Configure grid weights
        self.financial_frame.columnconfigure(0, weight=1)
        self.financial_frame.rowconfigure(1, weight=1)
    
    def create_financial_summary_ui(self, parent):
        """Create financial summary UI elements"""
        # Sales metrics
        sales_frame = ttk.LabelFrame(parent, text="Sales Metrics", padding="10")
        sales_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.total_sales_label = ttk.Label(sales_frame, text="Total Sales: -", font=('Arial', 12, 'bold'))
        self.total_sales_label.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.total_revenue_label = ttk.Label(sales_frame, text="Total Revenue: -", font=('Arial', 12, 'bold'))
        self.total_revenue_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        self.avg_sale_label = ttk.Label(sales_frame, text="Average Sale: -")
        self.avg_sale_label.grid(row=2, column=0, sticky=tk.W, pady=2)
        
        self.total_tax_label = ttk.Label(sales_frame, text="Total Tax: -")
        self.total_tax_label.grid(row=3, column=0, sticky=tk.W, pady=2)
        
        # Payment methods
        payment_frame = ttk.LabelFrame(parent, text="Payment Methods", padding="10")
        payment_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        self.cash_sales_label = ttk.Label(payment_frame, text="Cash Sales: -")
        self.cash_sales_label.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.card_sales_label = ttk.Label(payment_frame, text="Card Sales: -")
        self.card_sales_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        self.credit_sales_label = ttk.Label(payment_frame, text="Credit Sales: -")
        self.credit_sales_label.grid(row=2, column=0, sticky=tk.W, pady=2)
        
        # Top products
        top_products_frame = ttk.LabelFrame(parent, text="Top 5 Products", padding="5")
        top_products_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        top_products_frame.columnconfigure(0, weight=1)
        top_products_frame.rowconfigure(0, weight=1)
        
        top_columns = ('Rank', 'Product', 'Quantity Sold', 'Revenue')
        self.top_products_tree = ttk.Treeview(top_products_frame, columns=top_columns, show='headings', height=6)
        
        for col in top_columns:
            self.top_products_tree.heading(col, text=col)
        
        self.top_products_tree.column('Rank', width=50, anchor='center')
        self.top_products_tree.column('Product', width=200, anchor='w')
        self.top_products_tree.column('Quantity Sold', width=100, anchor='center')
        self.top_products_tree.column('Revenue', width=100, anchor='e')
        
        self.top_products_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        top_scroll = ttk.Scrollbar(top_products_frame, orient=tk.VERTICAL, command=self.top_products_tree.yview)
        self.top_products_tree.configure(yscrollcommand=top_scroll.set)
        top_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
    
    # Date helper methods
    def set_today(self):
        today = date.today().strftime("%Y-%m-%d")
        self.from_date_var.set(today)
        self.to_date_var.set(today)
    
    def set_yesterday(self):
        yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        self.from_date_var.set(yesterday)
        self.to_date_var.set(yesterday)
    
    def set_this_week(self):
        today = date.today()
        start_week = today - timedelta(days=today.weekday())
        self.from_date_var.set(start_week.strftime("%Y-%m-%d"))
        self.to_date_var.set(today.strftime("%Y-%m-%d"))
    
    def set_this_month(self):
        today = date.today()
        start_month = today.replace(day=1)
        self.from_date_var.set(start_month.strftime("%Y-%m-%d"))
        self.to_date_var.set(today.strftime("%Y-%m-%d"))
    
    def on_period_change(self, event):
        """Handle financial period change"""
        if self.fin_period_var.get() == "Custom":
            self.custom_date_frame.grid()
        else:
            self.custom_date_frame.grid_remove()
    
    def load_categories(self):
        """Load categories for inventory filter"""
        session = db_manager.get_session()
        try:
            categories = session.query(Category).order_by(Category.name).all()
            category_names = ["All Categories"] + [cat.name for cat in categories]
            self.inv_category_combo['values'] = category_names
            self.inv_category_combo.set("All Categories")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load categories: {e}")
        finally:
            session.close()
    
    # Report generation methods
    def generate_sales_report(self):
        """Generate sales report"""
        try:
            from_dt = datetime.strptime(f"{self.from_date_var.get()} {self.from_time_var.get()}", "%Y-%m-%d %H:%M")
            to_dt = datetime.strptime(f"{self.to_date_var.get()} {self.to_time_var.get()}", "%Y-%m-%d %H:%M")

            session = db_manager.get_session()
            try:
                # Query sales in datetime range
                sales = session.query(Sale).filter(
                    Sale.created_at >= from_dt,
                    Sale.created_at <= to_dt,
                ).order_by(Sale.created_at.desc()).all()
                
                # Clear existing data
                for item in self.sales_tree.get_children():
                    self.sales_tree.delete(item)
                
                # Clear summary
                for widget in self.sales_summary_frame.winfo_children():
                    widget.destroy()
                
                if not sales:
                    ttk.Label(self.sales_summary_frame, text="No sales found for the selected date range.", 
                             font=('Arial', 12)).pack()
                    return
                
                # Calculate summary
                total_sales = len(sales)
                total_amount = sum(sale.total_amount for sale in sales)
                total_tax = sum(sale.tax_amount for sale in sales)
                total_items = sum(len(sale.sale_items) for sale in sales)
                
                currency = DatabaseUtils.get_setting_value('currency', 'FCFA')
                
                # Display summary
                summary_text = f"Total Sales: {total_sales} | Total Amount: {total_amount:,.0f} {currency} | Total Tax: {total_tax:,.0f} {currency} | Items Sold: {total_items}"
                ttk.Label(self.sales_summary_frame, text=summary_text, font=('Arial', 12, 'bold')).pack()
                
                # Populate treeview
                for sale in sales:
                    customer_name = sale.customer.name if sale.customer else "Walk-in"
                    if len(customer_name) > 15:
                        customer_name = customer_name[:12] + "..."
                    
                    values = (
                        sale.created_at.strftime('%Y-%m-%d'),
                        sale.sale_number,
                        customer_name,
                        len(sale.sale_items),
                        f"{sale.subtotal:,.0f}",
                        f"{sale.tax_amount:,.0f}",
                        f"{sale.total_amount:,.0f}",
                        sale.payment_method.title()
                    )
                    self.sales_tree.insert('', tk.END, values=values)
                
            finally:
                session.close()
                
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter valid dates in YYYY-MM-DD format.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate sales report: {e}")
    
    def generate_inventory_report(self):
        """Generate inventory report"""
        try:
            report_type = self.inv_report_type.get()
            category_filter = self.inv_category_var.get()
            
            session = db_manager.get_session()
            try:
                # Build query
                query = session.query(Product).filter(Product.is_active == True)
                
                if category_filter != "All Categories":
                    category = session.query(Category).filter(Category.name == category_filter).first()
                    if category:
                        query = query.filter(Product.category_id == category.id)
                
                # Apply report type filter
                if report_type == "Low Stock Items":
                    query = query.filter(Product.stock_quantity <= Product.min_stock_level)
                elif report_type == "Out of Stock":
                    query = query.filter(Product.stock_quantity <= 0)
                
                products = query.order_by(Product.name).all()
                
                # Clear existing data
                for item in self.inventory_tree.get_children():
                    self.inventory_tree.delete(item)
                
                # Clear summary
                for widget in self.inv_summary_frame.winfo_children():
                    widget.destroy()
                
                if not products:
                    ttk.Label(self.inv_summary_frame, text="No products found for the selected criteria.", 
                             font=('Arial', 12)).pack()
                    return
                
                # Calculate summary
                total_products = len(products)
                total_stock_value = sum(product.stock_quantity * product.cost_price for product in products)
                total_retail_value = sum(product.stock_quantity * product.selling_price for product in products)
                low_stock_count = sum(1 for product in products if product.stock_quantity <= product.min_stock_level)
                
                currency = DatabaseUtils.get_setting_value('currency', 'FCFA')
                
                # Display summary
                summary_text = f"Products: {total_products} | Low Stock: {low_stock_count} | Stock Value (Cost): {total_stock_value:,.0f} {currency} | Stock Value (Retail): {total_retail_value:,.0f} {currency}"
                ttk.Label(self.inv_summary_frame, text=summary_text, font=('Arial', 12, 'bold')).pack()
                
                # Populate treeview
                for product in products:
                    category_name = product.category.name if product.category else "N/A"
                    stock_value = product.stock_quantity * product.selling_price
                    
                    values = (
                        product.id,
                        product.name,
                        category_name,
                        product.unit,
                        product.stock_quantity,
                        product.min_stock_level,
                        f"{product.cost_price:,.0f}",
                        f"{product.selling_price:,.0f}",
                        f"{stock_value:,.0f}"
                    )
                    
                    item_id = self.inventory_tree.insert('', tk.END, values=values)
                    
                    # Highlight low stock items
                    if product.stock_quantity <= product.min_stock_level:
                        self.inventory_tree.item(item_id, tags=('low_stock',))
                
                # Configure tags
                self.inventory_tree.tag_configure('low_stock', background='#ffeeee', foreground='red')
                
            finally:
                session.close()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate inventory report: {e}")
    
    def generate_performance_report(self):
        """Generate product performance report"""
        try:
            from_date = datetime.strptime(self.perf_from_date.get(), "%Y-%m-%d")
            to_date = datetime.strptime(self.perf_to_date.get(), "%Y-%m-%d")

            # Convert to full day range
            start_dt = from_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_dt = to_date.replace(hour=23, minute=59, second=59, microsecond=999999)

            sort_by = self.perf_sort_var.get()

            session = db_manager.get_session()
            try:
                # Query sale items in date range with product info
                from sqlalchemy import func

                query = session.query(
                    Product.id,
                    Product.name,
                    Category.name.label('category_name'),
                    func.sum(SaleItem.quantity).label('total_quantity'),
                    func.count(SaleItem.id).label('times_sold'),
                    func.sum(SaleItem.total_price).label('total_revenue'),
                    func.avg(SaleItem.unit_price).label('avg_price'),
                    func.max(Sale.created_at).label('last_sold')
                ).select_from(SaleItem)\
                .join(Product, SaleItem.product_id == Product.id)\
                .join(Sale, SaleItem.sale_id == Sale.id)\
                .outerjoin(Category, Product.category_id == Category.id)\
                .filter(
                    Sale.created_at >= start_dt,
                    Sale.created_at <= end_dt
                ).group_by(Product.id, Product.name, Category.name)

                # Apply sorting
                if sort_by == "Quantity Sold":
                    query = query.order_by(func.sum(SaleItem.quantity).desc())
                elif sort_by == "Revenue":
                    query = query.order_by(func.sum(SaleItem.total_price).desc())
                elif sort_by == "Times Sold":
                    query = query.order_by(func.count(SaleItem.id).desc())
                else:  # Profit
                    query = query.order_by(func.sum(SaleItem.total_price).desc())

                results = query.all()

                # Clear existing data
                for item in self.performance_tree.get_children():
                    self.performance_tree.delete(item)

                if not results:
                    messagebox.showinfo("No Data", "No sales found for the selected date range.")
                    return

                # Populate treeview
                for rank, result in enumerate(results, 1):
                    last_sold = result.last_sold.strftime('%Y-%m-%d') if result.last_sold else "N/A"

                    values = (
                        rank,
                        result.name,
                        result.category_name or "N/A",
                        f"{result.total_quantity:,.1f}",
                        result.times_sold,
                        f"{result.total_revenue:,.0f}",
                        f"{result.avg_price:,.0f}",
                        last_sold
                    )
                    self.performance_tree.insert('', tk.END, values=values)

            finally:
                session.close()

        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter valid dates in YYYY-MM-DD format.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate performance report: {e}")
    
    def generate_financial_summary(self):
        """Generate financial summary"""
        try:
            # Determine date range based on period selection
            period = self.fin_period_var.get()
            today = date.today()
            
            if period == "Today":
                from_date = to_date = today
            elif period == "This Week":
                from_date = today - timedelta(days=today.weekday())
                to_date = today
            elif period == "This Month":
                from_date = today.replace(day=1)
                to_date = today
            elif period == "Last Month":
                last_month = today.replace(day=1) - timedelta(days=1)
                from_date = last_month.replace(day=1)
                to_date = last_month
            elif period == "This Year":
                from_date = today.replace(month=1, day=1)
                to_date = today
            else:  # Custom
                from_date = datetime.strptime(self.fin_from_date.get(), "%Y-%m-%d").date()
                to_date = datetime.strptime(self.fin_to_date.get(), "%Y-%m-%d").date()

            # Convert to full day range
            start_dt = datetime.combine(from_date, datetime.min.time())
            end_dt = datetime.combine(to_date, datetime.max.time())

            session = db_manager.get_session()
            try:
                # Query sales in date range
                sales = session.query(Sale).filter(
                    Sale.created_at >= start_dt,
                    Sale.created_at <= end_dt
                ).all()
                
                if not sales:
                    # Clear all labels
                    self.total_sales_label.config(text="Total Sales: 0")
                    self.total_revenue_label.config(text="Total Revenue: 0")
                    self.avg_sale_label.config(text="Average Sale: 0")
                    self.total_tax_label.config(text="Total Tax: 0")
                    self.cash_sales_label.config(text="Cash Sales: 0")
                    self.card_sales_label.config(text="Card Sales: 0")
                    self.credit_sales_label.config(text="Credit Sales: 0")
                    
                    # Clear top products
                    for item in self.top_products_tree.get_children():
                        self.top_products_tree.delete(item)
                    
                    messagebox.showinfo("No Data", "No sales found for the selected period.")
                    return
                
                # Calculate metrics
                total_sales = len(sales)
                total_revenue = sum(sale.total_amount for sale in sales)
                total_tax = sum(sale.tax_amount for sale in sales)
                avg_sale = total_revenue / total_sales if total_sales > 0 else 0
                
                # Payment method breakdown
                cash_sales = sum(sale.total_amount for sale in sales if sale.payment_method == 'cash')
                card_sales = sum(sale.total_amount for sale in sales if sale.payment_method == 'card')
                credit_sales = sum(sale.total_amount for sale in sales if sale.payment_method == 'credit')
                
                currency = DatabaseUtils.get_setting_value('currency', 'FCFA')
                
                # Update labels
                self.total_sales_label.config(text=f"Total Sales: {total_sales}")
                self.total_revenue_label.config(text=f"Total Revenue: {total_revenue:,.0f} {currency}")
                self.avg_sale_label.config(text=f"Average Sale: {avg_sale:,.0f} {currency}")
                self.total_tax_label.config(text=f"Total Tax: {total_tax:,.0f} {currency}")
                self.cash_sales_label.config(text=f"Cash Sales: {cash_sales:,.0f} {currency}")
                self.card_sales_label.config(text=f"Card Sales: {card_sales:,.0f} {currency}")
                self.credit_sales_label.config(text=f"Credit Sales: {credit_sales:,.0f} {currency}")
                
                # Get top 5 products
                from sqlalchemy import func
                
                top_products = session.query(
                    Product.name,
                    func.sum(SaleItem.quantity).label('total_quantity'),
                    func.sum(SaleItem.total_price).label('total_revenue')
                ).select_from(SaleItem)\
                .join(Product, SaleItem.product_id == Product.id)\
                .join(Sale, SaleItem.sale_id == Sale.id)\
                .filter(
                    Sale.created_at >= start_dt,
                    Sale.created_at <= end_dt
                ).group_by(Product.id, Product.name)\
                .order_by(func.sum(SaleItem.total_price).desc())\
                .limit(5).all()
                
                # Clear and populate top products
                for item in self.top_products_tree.get_children():
                    self.top_products_tree.delete(item)
                
                for rank, product in enumerate(top_products, 1):
                    values = (
                        rank,
                        product.name,
                        f"{product.total_quantity:,.1f}",
                        f"{product.total_revenue:,.0f}"
                    )
                    self.top_products_tree.insert('', tk.END, values=values)
                
            finally:
                session.close()
                
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter valid dates in YYYY-MM-DD format.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate financial summary: {e}")
    
    # Export methods
    def export_sales_csv(self):
        """Export sales report to CSV"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Save Sales Report"
            )
            
            if not filename:
                return
            
            # Get current tree data
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                headers = ['Date', 'Receipt #', 'Customer', 'Items', 'Subtotal', 'Tax', 'Total', 'Payment']
                writer.writerow(headers)
                
                # Write data
                for child in self.sales_tree.get_children():
                    values = self.sales_tree.item(child)['values']
                    writer.writerow(values)
            
            messagebox.showinfo("Export Complete", f"Sales report exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export sales report: {e}")
    
    def export_inventory_csv(self):
        """Export inventory report to CSV"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Save Inventory Report"
            )
            
            if not filename:
                return
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                headers = ['ID', 'Product', 'Category', 'Unit', 'Stock', 'Min Stock', 'Cost Price', 'Selling Price', 'Value']
                writer.writerow(headers)
                
                # Write data
                for child in self.inventory_tree.get_children():
                    values = self.inventory_tree.item(child)['values']
                    writer.writerow(values)
            
            messagebox.showinfo("Export Complete", f"Inventory report exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export inventory report: {e}")
    
    def export_performance_csv(self):
        """Export performance report to CSV"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Save Performance Report"
            )
            
            if not filename:
                return
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                headers = ['Rank', 'Product', 'Category', 'Qty Sold', 'Times Sold', 'Revenue', 'Avg Price', 'Last Sold']
                writer.writerow(headers)
                
                # Write data
                for child in self.performance_tree.get_children():
                    values = self.performance_tree.item(child)['values']
                    writer.writerow(values)
            
            messagebox.showinfo("Export Complete", f"Performance report exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export performance report: {e}")
    
    def export_financial_csv(self):
        """Export financial summary to CSV"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Save Financial Summary"
            )
            
            if not filename:
                return
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write summary data
                writer.writerow(["Financial Summary"])
                writer.writerow(["Period", self.fin_period_var.get()])
                writer.writerow([])
                
                # Sales metrics
                writer.writerow(["Sales Metrics"])
                writer.writerow(["Total Sales", self.total_sales_label.cget("text").split(": ")[1]])
                writer.writerow(["Total Revenue", self.total_revenue_label.cget("text").split(": ")[1]])
                writer.writerow(["Average Sale", self.avg_sale_label.cget("text").split(": ")[1]])
                writer.writerow(["Total Tax", self.total_tax_label.cget("text").split(": ")[1]])
                writer.writerow([])
                
                # Payment methods
                writer.writerow(["Payment Methods"])
                writer.writerow(["Cash Sales", self.cash_sales_label.cget("text").split(": ")[1]])
                writer.writerow(["Card Sales", self.card_sales_label.cget("text").split(": ")[1]])
                writer.writerow(["Credit Sales", self.credit_sales_label.cget("text").split(": ")[1]])
                writer.writerow([])
                
                # Top products
                writer.writerow(["Top 5 Products"])
                writer.writerow(["Rank", "Product", "Quantity Sold", "Revenue"])
                for child in self.top_products_tree.get_children():
                    values = self.top_products_tree.item(child)['values']
                    writer.writerow(values)
            
            messagebox.showinfo("Export Complete", f"Financial summary exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export financial summary: {e}")
    
    def print_sales_report(self):
        """Print sales report"""
        try:
            from utils.receipt_printer import ReceiptPrinter
            printer = ReceiptPrinter()
            
            # Generate a simple sales report (you can enhance this)
            messagebox.showinfo("Print", "Print functionality coming soon!")
            
        except Exception as e:
            messagebox.showerror("Print Error", f"Failed to print report: {e}")
    
    def print_inventory_report(self):
        """Print inventory report"""
        try:
            messagebox.showinfo("Print", "Print functionality coming soon!")
            
        except Exception as e:
            messagebox.showerror("Print Error", f"Failed to print report: {e}")