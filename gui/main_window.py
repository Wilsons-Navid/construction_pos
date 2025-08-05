# # gui/main_window.py
# import tkinter as tk
# from tkinter import ttk
# from datetime import datetime
# from .pos_window import POSWindow
# from .inventory_window import InventoryWindow
# from .reports_window import ReportsWindow

# class MainWindow:
#     def __init__(self, root):
#         self.root = root
#         self.current_window = None
        
#         # Create main container
#         self.main_frame = ttk.Frame(root, padding="10")
#         self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
#         # Configure grid weights
#         root.columnconfigure(0, weight=1)
#         root.rowconfigure(0, weight=1)
#         self.main_frame.columnconfigure(1, weight=1)
#         self.main_frame.rowconfigure(1, weight=1)
        
#         self.setup_ui()
        
#         # Show POS by default
#         self.show_pos()
    
#     def setup_ui(self):
#         """Setup main UI components"""
#         # Header
#         self.create_header()
        
#         # Sidebar navigation
#         self.create_sidebar()
        
#         # Content area
#         self.content_frame = ttk.Frame(self.main_frame)
#         self.content_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
#         self.content_frame.columnconfigure(0, weight=1)
#         self.content_frame.rowconfigure(0, weight=1)
        
#         # Status bar
#         self.create_status_bar()
        
#     def create_header(self):
#         """Create header with title and current time"""
#         header_frame = ttk.Frame(self.main_frame)
#         header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
#         header_frame.columnconfigure(1, weight=1)
        
#         # Title
#         title_label = ttk.Label(
#             header_frame, 
#             text="Construction Materials POS", 
#             style='Title.TLabel'
#         )
#         title_label.grid(row=0, column=0, sticky=tk.W)
        
#         # Current time
#         self.time_label = ttk.Label(header_frame, text="", font=('Arial', 10))
#         self.time_label.grid(row=0, column=2, sticky=tk.E)
        
#         # Update time
#         self.update_time()
    
#     def create_sidebar(self):
#         """Create navigation sidebar"""
#         sidebar_frame = ttk.LabelFrame(self.main_frame, text="Navigation", padding="10")
#         sidebar_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 10))
        
#         # Navigation buttons
#         nav_buttons = [
#             ("🛒 Point of Sale", self.show_pos, "Large.TButton"),
#             ("📦 Inventory", self.show_inventory, "Large.TButton"),
#             ("📊 Reports", self.show_reports, "Large.TButton"),
#             ("👥 Customers", self.show_customers, "Large.TButton"),
#             ("⚙️ Settings", self.show_settings, "Large.TButton")
#         ]
        
#         for i, (text, command, style) in enumerate(nav_buttons):
#             btn = ttk.Button(
#                 sidebar_frame, 
#                 text=text, 
#                 command=command,
#                 style=style,
#                 width=15
#             )
#             btn.grid(row=i, column=0, pady=5, sticky=(tk.W, tk.E))
        
#         # Quick stats
#         self.create_quick_stats(sidebar_frame)
    
#     def create_quick_stats(self, parent):
#         """Create quick statistics display"""
#         stats_frame = ttk.LabelFrame(parent, text="Quick Stats", padding="5")
#         stats_frame.grid(row=len(parent.winfo_children()), column=0, sticky=(tk.W, tk.E), pady=(20, 0))
        
#         from database.database import db_manager
#         from database.models import Product, Sale
#         from datetime import date
        
#         session = db_manager.get_session()
#         try:
#             # Today's sales
#             today = date.today()
#             today_sales = session.query(Sale).filter(
#                 Sale.created_at >= today
#             ).count()
            
#             # Low stock items
#             low_stock = session.query(Product).filter(
#                 Product.stock_quantity <= Product.min_stock_level
#             ).count()
            
#             # Total products
#             total_products = session.query(Product).filter(Product.is_active == True).count()
            
#         except Exception as e:
#             today_sales = 0
#             low_stock = 0
#             total_products = 0
#         finally:
#             session.close()
        
#         # Display stats
#         stats_data = [
#             ("Today's Sales:", str(today_sales)),
#             ("Low Stock Items:", str(low_stock)),
#             ("Total Products:", str(total_products))
#         ]
        
#         for i, (label, value) in enumerate(stats_data):
#             ttk.Label(stats_frame, text=label, font=('Arial', 9)).grid(row=i, column=0, sticky=tk.W)
#             ttk.Label(stats_frame, text=value, font=('Arial', 9, 'bold')).grid(row=i, column=1, sticky=tk.E)
    
#     def create_status_bar(self):
#         """Create status bar"""
#         self.status_frame = ttk.Frame(self.main_frame)
#         self.status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
#         self.status_frame.columnconfigure(0, weight=1)
        
#         self.status_label = ttk.Label(self.status_frame, text="Ready", relief=tk.SUNKEN)
#         self.status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
    
#     def update_time(self):
#         """Update current time display"""
#         current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         self.time_label.config(text=current_time)
#         self.root.after(1000, self.update_time)  # Update every second
    
#     def clear_content(self):
#         """Clear current content area"""
#         for widget in self.content_frame.winfo_children():
#             widget.destroy()
    
#     def show_pos(self):
#         """Show POS window"""
#         self.clear_content()
#         self.current_window = POSWindow(self.content_frame)
#         self.update_status("Point of Sale - Ready")
    
#     def show_inventory(self):
#         """Show inventory management window"""
#         self.clear_content()
#         self.current_window = InventoryWindow(self.content_frame)
#         self.update_status("Inventory Management")
    
#     def show_reports(self):
#         """Show reports window"""
#         self.clear_content()
#         self.current_window = ReportsWindow(self.content_frame)
#         self.update_status("Reports & Analytics")
    
#     def show_customers(self):
#         """Show customer management window"""
#         self.clear_content()
#         # Customer management will be implemented here
#         placeholder = ttk.Label(
#             self.content_frame, 
#             text="Customer Management\n(Coming Soon)", 
#             font=('Arial', 16),
#             anchor='center'
#         )
#         placeholder.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
#         self.update_status("Customer Management")
    
#     def show_settings(self):
#         """Show settings window"""
#         self.clear_content()
#         # Settings will be implemented here
#         placeholder = ttk.Label(
#             self.content_frame, 
#             text="Settings\n(Coming Soon)", 
#             font=('Arial', 16),
#             anchor='center'
#         )
#         placeholder.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
#         self.update_status("Settings")
    
#     def update_status(self, message):
#         """Update status bar message"""
#         self.status_label.config(text=message)
# gui/main_window.py - POLISHED VERSION
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from .pos_window import POSWindow
from .inventory_window import InventoryWindow
from .reports_window import ReportsWindow

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.current_window = None
        
        # Configure root window
        self.setup_window_properties()
        
        # Create main container with modern styling
        self.main_frame = ttk.Frame(root, padding="0")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # Setup modern UI
        self.setup_modern_ui()
        
        # Show POS by default
        self.show_pos()
    
    def setup_window_properties(self):
        """Setup modern window properties"""
        # Set minimum size
        self.root.minsize(1000, 700)
        
        # Configure window icon (if available)
        try:
            self.root.iconbitmap(default='icon.ico')
        except:
            pass
        
        # Center window on screen
        self.center_window()
    
    def center_window(self):
        """Center window on screen"""
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate position
        x = (screen_width - 1200) // 2
        y = (screen_height - 800) // 2
        
        # Set geometry
        self.root.geometry(f"1200x800+{x}+{y}")
    
    def setup_modern_ui(self):
        """Setup modern UI components"""
        # Modern header
        self.create_modern_header()
        
        # Modern sidebar navigation
        self.create_modern_sidebar()
        
        # Modern content area
        self.content_frame = ttk.Frame(self.main_frame, style='Content.TFrame')
        self.content_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(1, 0))
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)
        
        # Modern status bar
        self.create_modern_status_bar()
        
    def create_modern_header(self):
        """Create modern header with gradient-like appearance"""
        header_frame = ttk.Frame(self.main_frame, style='Header.TFrame', padding="20 15")
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        header_frame.columnconfigure(1, weight=1)
        
        # App title with modern styling
        title_label = ttk.Label(
            header_frame, 
            text="🏗️ Construction Materials POS", 
            style='Title.TLabel'
        )
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Subtitle
        subtitle_label = ttk.Label(
            header_frame, 
            text="Professional Point of Sale System", 
            style='Subtitle.TLabel'
        )
        subtitle_label.grid(row=1, column=0, sticky=tk.W, pady=(2, 0))
        
        # Modern time display
        time_frame = ttk.Frame(header_frame)
        time_frame.grid(row=0, column=2, rowspan=2, sticky=tk.E)
        
        self.time_label = ttk.Label(time_frame, text="", style='Time.TLabel')
        self.time_label.pack()
        
        self.date_label = ttk.Label(time_frame, text="", style='Date.TLabel')
        self.date_label.pack()
        
        # Update time
        self.update_time()
    
    def create_modern_sidebar(self):
        """Create modern navigation sidebar"""
        sidebar_frame = ttk.Frame(self.main_frame, style='Sidebar.TFrame', padding="0")
        sidebar_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        sidebar_frame.columnconfigure(0, weight=1)
        
        # Navigation title
        nav_title = ttk.Label(sidebar_frame, text="NAVIGATION", style='NavTitle.TLabel')
        nav_title.grid(row=0, column=0, pady=(20, 10), padx=20)
        
        # Modern navigation buttons
        nav_buttons = [
            ("💳", "Point of Sale", self.show_pos, "POS.TButton"),
            ("📦", "Inventory", self.show_inventory, "Nav.TButton"),
            ("📊", "Reports", self.show_reports, "Nav.TButton"),
            ("👥", "Customers", self.show_customers, "Nav.TButton"),
            ("⚙️", "Settings", self.show_settings, "Nav.TButton")
        ]
        
        self.nav_buttons = {}
        for i, (icon, text, command, style) in enumerate(nav_buttons):
            btn_frame = ttk.Frame(sidebar_frame)
            btn_frame.grid(row=i+1, column=0, sticky=(tk.W, tk.E), padx=10, pady=2)
            btn_frame.columnconfigure(0, weight=1)
            
            btn = ttk.Button(
                btn_frame, 
                text=f"{icon}  {text}", 
                command=command,
                style=style,
                width=20
            )
            btn.grid(row=0, column=0, sticky=(tk.W, tk.E))
            self.nav_buttons[text] = btn
        
        # Set initial active button
        self.set_active_nav_button("Point of Sale")
        
        # Modern quick stats section
        self.create_modern_quick_stats(sidebar_frame)
    
    def create_modern_quick_stats(self, parent):
        """Create modern quick statistics display"""
        stats_frame = ttk.LabelFrame(parent, text="📈 TODAY'S OVERVIEW", style='Stats.TLabelframe', padding="15")
        stats_frame.grid(row=len(parent.winfo_children()), column=0, sticky=(tk.W, tk.E), padx=10, pady=(30, 10))
        stats_frame.columnconfigure(1, weight=1)
        
        # Get statistics
        from database.database import db_manager
        from database.models import Product, Sale
        from datetime import date
        
        session = db_manager.get_session()
        try:
            if session:
                # Today's sales
                today = date.today()
                today_sales = session.query(Sale).filter(
                    Sale.created_at >= today
                ).count()
                
                # Today's revenue
                today_revenue_result = session.query(Sale).filter(
                    Sale.created_at >= today
                ).all()
                today_revenue = sum(sale.total_amount for sale in today_revenue_result)
                
                # Low stock items
                low_stock = session.query(Product).filter(
                    Product.stock_quantity <= Product.min_stock_level,
                    Product.is_active == True
                ).count()
                
                # Total active products
                total_products = session.query(Product).filter(Product.is_active == True).count()
                
            else:
                today_sales = 0
                today_revenue = 0
                low_stock = 0
                total_products = 0
                
        except Exception as e:
            print(f"Error getting stats: {e}")
            today_sales = 0
            today_revenue = 0
            low_stock = 0
            total_products = 0
        finally:
            if session:
                session.close()
        
        # Display stats with modern styling
        stats_data = [
            ("💰", "Sales Today", str(today_sales), "StatValue.TLabel"),
            ("💵", "Revenue", f"{today_revenue:,.0f}", "StatValue.TLabel"),
            ("⚠️", "Low Stock", str(low_stock), "StatAlert.TLabel" if low_stock > 0 else "StatValue.TLabel"),
            ("📊", "Products", str(total_products), "StatValue.TLabel")
        ]
        
        for i, (icon, label, value, style) in enumerate(stats_data):
            # Icon and label
            label_text = f"{icon} {label}"
            ttk.Label(stats_frame, text=label_text, style='StatLabel.TLabel').grid(
                row=i, column=0, sticky=tk.W, pady=3
            )
            
            # Value
            ttk.Label(stats_frame, text=value, style=style).grid(
                row=i, column=1, sticky=tk.E, pady=3
            )
    
    def create_modern_status_bar(self):
        """Create modern status bar"""
        self.status_frame = ttk.Frame(self.main_frame, style='StatusBar.TFrame', padding="10 5")
        self.status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        self.status_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(self.status_frame, text="Ready", style='Status.TLabel')
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Version info
        version_label = ttk.Label(self.status_frame, text="v1.0", style='Version.TLabel')
        version_label.grid(row=0, column=1, sticky=tk.E)
    
    def set_active_nav_button(self, active_text):
        """Set active navigation button styling"""
        for text, button in self.nav_buttons.items():
            if text == active_text:
                button.configure(style='POSActive.TButton' if text == "Point of Sale" else 'NavActive.TButton')
            else:
                button.configure(style='POS.TButton' if text == "Point of Sale" else 'Nav.TButton')
    
    def update_time(self):
        """Update current time display"""
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_date = now.strftime("%A, %B %d, %Y")
        
        self.time_label.config(text=current_time)
        self.date_label.config(text=current_date)
        self.root.after(1000, self.update_time)  # Update every second
    
    def clear_content(self):
        """Clear current content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_pos(self):
        """Show POS window"""
        self.clear_content()
        self.current_window = POSWindow(self.content_frame)
        self.update_status("Point of Sale - Processing transactions")
        self.set_active_nav_button("Point of Sale")
    
    def show_inventory(self):
        """Show inventory management window"""
        self.clear_content()
        self.current_window = InventoryWindow(self.content_frame)
        self.update_status("Inventory Management - Managing products and stock")
        self.set_active_nav_button("Inventory")
    
    def show_reports(self):
        """Show reports window"""
        self.clear_content()
        self.current_window = ReportsWindow(self.content_frame)
        self.update_status("Reports & Analytics - Viewing business insights")
        self.set_active_nav_button("Reports")
    
    def show_customers(self):
        """Show customer management window"""
        self.clear_content()
        self.set_active_nav_button("Customers")
        
        # Modern placeholder
        placeholder_frame = ttk.Frame(self.content_frame, style='Content.TFrame')
        placeholder_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        placeholder_frame.columnconfigure(0, weight=1)
        placeholder_frame.rowconfigure(1, weight=1)
        
        # Icon and title
        ttk.Label(
            placeholder_frame, 
            text="👥", 
            font=('Arial', 48)
        ).grid(row=0, column=0, pady=(50, 10))
        
        ttk.Label(
            placeholder_frame, 
            text="Customer Management", 
            style='PlaceholderTitle.TLabel'
        ).grid(row=1, column=0, pady=10)
        
        ttk.Label(
            placeholder_frame, 
            text="Advanced customer features coming soon!\nFor now, basic customer selection is available in POS.", 
            style='PlaceholderText.TLabel'
        ).grid(row=2, column=0, pady=10)
        
        self.update_status("Customer Management - Feature in development")
    
    def show_settings(self):
        """Show settings window"""
        self.clear_content()
        self.set_active_nav_button("Settings")
        
        # Modern placeholder  
        placeholder_frame = ttk.Frame(self.content_frame, style='Content.TFrame')
        placeholder_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        placeholder_frame.columnconfigure(0, weight=1)
        placeholder_frame.rowconfigure(1, weight=1)
        
        # Icon and title
        ttk.Label(
            placeholder_frame, 
            text="⚙️", 
            font=('Arial', 48)
        ).grid(row=0, column=0, pady=(50, 10))
        
        ttk.Label(
            placeholder_frame, 
            text="System Settings", 
            style='PlaceholderTitle.TLabel'
        ).grid(row=1, column=0, pady=10)
        
        ttk.Label(
            placeholder_frame, 
            text="Configuration options coming soon!\nCurrent settings are automatically optimized.", 
            style='PlaceholderText.TLabel'
        ).grid(row=2, column=0, pady=10)
        
        self.update_status("Settings - System configuration")
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_label.config(text=message)