# # main.py - Fixed for PyInstaller compatibility
# import tkinter as tk
# from tkinter import ttk, messagebox
# import sys
# import os
# from datetime import datetime

# # Add current directory to path for both development and compiled versions
# if getattr(sys, 'frozen', False):
#     # Running as compiled executable
#     current_dir = os.path.dirname(sys.executable)
#     sys.path.insert(0, current_dir)
# else:
#     # Running as script
#     current_dir = os.path.dirname(os.path.abspath(__file__))
#     sys.path.insert(0, current_dir)

# # Try different import methods
# try:
#     # Try relative imports first (development)
#     from database.database import init_database, db_manager, DatabaseUtils
#     from database.models import *
#     from gui.main_window import MainWindow
# except ImportError:
#     try:
#         # Try direct imports (compiled)
#         import database.database as db_module
#         from database.database import init_database, db_manager, DatabaseUtils
#         from database.models import *
#         import gui.main_window as main_window_module
#         from gui.main_window import MainWindow
#     except ImportError:
#         # Last resort - add all subdirectories to path
#         subdirs = ['database', 'gui', 'utils']
#         for subdir in subdirs:
#             subdir_path = os.path.join(current_dir, subdir)
#             if os.path.exists(subdir_path):
#                 sys.path.insert(0, subdir_path)
        
#         # Try imports again
#         try:
#             from database import init_database, db_manager, DatabaseUtils
#             from models import *
#             from main_window import MainWindow
#         except ImportError as e:
#             messagebox.showerror("Import Error", 
#                                f"Failed to import required modules: {e}\n"
#                                f"Current directory: {current_dir}\n"
#                                f"Python path: {sys.path}")
#             sys.exit(1)

# class ConstructionPOSApp:
#     def __init__(self):
#         self.root = tk.Tk()
#         self.root.title("Construction Materials POS System")
#         self.root.geometry("1200x800")
        
#         # Try to maximize window
#         try:
#             self.root.state('zoomed')  # Windows
#         except:
#             try:
#                 self.root.attributes('-zoomed', True)  # Linux
#             except:
#                 pass  # Mac or other systems
        
#         # Initialize database
#         self.init_database()
        
#         # Load and apply theme
#         self.setup_theme()
        
#         # Create main window
#         self.main_window = MainWindow(self.root)
        
#         # Setup menu
#         self.setup_menu()
        
#     def init_database(self):
#         """Initialize database and add sample data if needed"""
#         try:
#             init_database()
#             self.add_sample_data()
#             print("Database initialized successfully!")
#         except Exception as e:
#             messagebox.showerror("Database Error", f"Failed to initialize database: {e}")
#             # Don't exit - try to continue
#             print(f"Database error: {e}")
    
#     def add_sample_data(self):
#         """Add sample data for testing"""
#         session = db_manager.get_session()
#         try:
#             # Import here to avoid circular imports
#             from database.models import Category, Product, Customer
            
#             # Check if we already have data
#             if session.query(Category).count() > 0:
#                 return
            
#             # Add categories
#             categories_data = [
#                 {"name": "Cement & Concrete", "description": "Cement, concrete mix, additives"},
#                 {"name": "Steel & Iron", "description": "Rebar, steel sheets, iron rods"},
#                 {"name": "Bricks & Blocks", "description": "Building bricks, concrete blocks"},
#                 {"name": "Roofing Materials", "description": "Roofing sheets, tiles, gutters"},
#                 {"name": "Plumbing", "description": "Pipes, fittings, fixtures"},
#                 {"name": "Electrical", "description": "Wires, switches, outlets"},
#                 {"name": "Tools & Hardware", "description": "Hand tools, fasteners, hardware"},
#                 {"name": "Paint & Finishes", "description": "Paints, brushes, finishing materials"}
#             ]
            
#             categories = []
#             for cat_data in categories_data:
#                 category = Category(**cat_data)
#                 session.add(category)
#                 categories.append(category)
            
#             session.flush()  # Get IDs
            
#             # Add sample products
#             products_data = [
#                 # Cement & Concrete
#                 {"name": "Portland Cement 50kg", "category_id": categories[0].id, "unit": "bag", 
#                  "cost_price": 4500, "selling_price": 5500, "stock_quantity": 100, "barcode": "CEM001"},
#                 {"name": "Ready Mix Concrete", "category_id": categories[0].id, "unit": "m3", 
#                  "cost_price": 85000, "selling_price": 95000, "stock_quantity": 50, "barcode": "CON001"},
                
#                 # Steel & Iron
#                 {"name": "Steel Rebar 12mm", "category_id": categories[1].id, "unit": "piece", 
#                  "cost_price": 8500, "selling_price": 9500, "stock_quantity": 200, "barcode": "STL001"},
#                 {"name": "Iron Sheet 26 Gauge", "category_id": categories[1].id, "unit": "sheet", 
#                  "cost_price": 15000, "selling_price": 17000, "stock_quantity": 75, "barcode": "IRN001"},
                
#                 # Bricks & Blocks
#                 {"name": "Red Building Brick", "category_id": categories[2].id, "unit": "piece", 
#                  "cost_price": 180, "selling_price": 220, "stock_quantity": 5000, "barcode": "BRK001"},
#                 {"name": "Concrete Block 8inch", "category_id": categories[2].id, "unit": "piece", 
#                  "cost_price": 450, "selling_price": 550, "stock_quantity": 800, "barcode": "BLK001"},
                
#                 # Roofing
#                 {"name": "Aluminum Roofing Sheet", "category_id": categories[3].id, "unit": "sheet", 
#                  "cost_price": 12000, "selling_price": 14000, "stock_quantity": 150, "barcode": "ROF001"},
                
#                 # Plumbing
#                 {"name": "PVC Pipe 4inch", "category_id": categories[4].id, "unit": "meter", 
#                  "cost_price": 850, "selling_price": 1000, "stock_quantity": 300, "barcode": "PVC001"},
                
#                 # Tools
#                 {"name": "Hammer 500g", "category_id": categories[6].id, "unit": "piece", 
#                  "cost_price": 2500, "selling_price": 3200, "stock_quantity": 25, "barcode": "HAM001"},
#                 {"name": "Screwdriver Set", "category_id": categories[6].id, "unit": "set", 
#                  "cost_price": 1800, "selling_price": 2500, "stock_quantity": 15, "barcode": "SCR001"}
#             ]
            
#             for prod_data in products_data:
#                 product = Product(**prod_data)
#                 session.add(product)
            
#             # Add default customer
#             default_customer = Customer(
#                 name="Walk-in Customer",
#                 phone="",
#                 email="",
#                 address="",
#                 credit_limit=0
#             )
#             session.add(default_customer)
            
#             session.commit()
#             print("Sample data added successfully!")
            
#         except Exception as e:
#             session.rollback()
#             print(f"Error adding sample data: {e}")
#         finally:
#             session.close()
    
#     def setup_theme(self):
#         """Setup application theme"""
#         style = ttk.Style()
        
#         # Try to use a modern theme
#         try:
#             style.theme_use('clam')
#         except:
#             pass  # Use default theme if clam not available
        
#         # Configure colors
#         style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
#         style.configure('Heading.TLabel', font=('Arial', 12, 'bold'))
#         style.configure('Large.TButton', font=('Arial', 12), padding=10)
        
#     def setup_menu(self):
#         """Setup application menu bar"""
#         menubar = tk.Menu(self.root)
#         self.root.config(menu=menubar)
        
#         # File menu
#         file_menu = tk.Menu(menubar, tearoff=0)
#         menubar.add_cascade(label="File", menu=file_menu)
#         file_menu.add_command(label="Backup Database", command=self.backup_database)
#         file_menu.add_separator()
#         file_menu.add_command(label="Exit", command=self.root.quit)
        
#         # View menu
#         view_menu = tk.Menu(menubar, tearoff=0)
#         menubar.add_cascade(label="View", menu=view_menu)
#         view_menu.add_command(label="POS", command=lambda: self.main_window.show_pos())
#         view_menu.add_command(label="Inventory", command=lambda: self.main_window.show_inventory())
#         view_menu.add_command(label="Reports", command=lambda: self.main_window.show_reports())
        
#         # Help menu
#         help_menu = tk.Menu(menubar, tearoff=0)
#         menubar.add_cascade(label="Help", menu=help_menu)
#         help_menu.add_command(label="About", command=self.show_about)
        
#     def backup_database(self):
#         """Create database backup"""
#         try:
#             backup_path = db_manager.backup_database()
#             messagebox.showinfo("Backup Complete", f"Database backed up to: {backup_path}")
#         except Exception as e:
#             messagebox.showerror("Backup Error", f"Failed to backup database: {e}")
    
#     def show_about(self):
#         """Show about dialog"""
#         about_text = """
# Construction Materials POS System
# Version 1.0

# An offline Point of Sale system designed for 
# construction material shops (quincailleries).

# Features:
# - Inventory Management
# - Sales Processing  
# - Customer Management
# - Reports & Analytics
# - Offline Operation

# Developed with Python & Tkinter
#         """
#         messagebox.showinfo("About", about_text)
    
#     def run(self):
#         """Start the application"""
#         try:
#             self.root.mainloop()
#         except KeyboardInterrupt:
#             print("Application stopped by user")
#         except Exception as e:
#             messagebox.showerror("Application Error", f"An error occurred: {e}")

# if __name__ == "__main__":
#     try:
#         app = ConstructionPOSApp()
#         app.run()
#     except Exception as e:
#         # Show error in message box if GUI fails
#         try:
#             root = tk.Tk()
#             root.withdraw()  # Hide main window
#             messagebox.showerror("Startup Error", f"Failed to start application: {e}")
#         except:
#             print(f"Critical error: {e}")
#         sys.exit(1)

# main.py - POLISHED VERSION
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from datetime import datetime

# Add current directory to path for both development and compiled versions
if getattr(sys, 'frozen', False):
    current_dir = os.path.dirname(sys.executable)
    sys.path.insert(0, current_dir)
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)

# Try different import methods
try:
    from database.database import init_database, db_manager, DatabaseUtils
    from database.models import *
    from gui.main_window import MainWindow
    from gui.login_window import LoginWindow
    from utils.auth import get_current_user
except ImportError:
    try:
        import database.database as db_module
        from database.database import init_database, db_manager, DatabaseUtils
        from database.models import *
        import gui.main_window as main_window_module
        from gui.main_window import MainWindow
        from gui.login_window import LoginWindow
        from utils.auth import get_current_user
    except ImportError:
        subdirs = ['database', 'gui', 'utils']
        for subdir in subdirs:
            subdir_path = os.path.join(current_dir, subdir)
            if os.path.exists(subdir_path):
                sys.path.insert(0, subdir_path)
        
        try:
            from database import init_database, db_manager, DatabaseUtils
            from models import *
            from main_window import MainWindow
            from login_window import LoginWindow
            from auth import get_current_user
        except ImportError as e:
            messagebox.showerror("Import Error", 
                               f"Failed to import required modules: {e}\n"
                               f"Current directory: {current_dir}")
            sys.exit(1)

class ConstructionPOSApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Construction Materials POS System")
        self.root.geometry("1200x800")
        
        # Try to maximize window
        try:
            self.root.state('zoomed')  # Windows
        except:
            try:
                self.root.attributes('-zoomed', True)  # Linux
            except:
                pass  # Mac or other systems
        
        # Initialize database
        self.init_database()

        # Show login window before proceeding
        if not self.show_login():
            self.root.destroy()
            self.root = None
            return

        # Setup modern theme
        self.setup_modern_theme()

        # Create main window
        self.main_window = MainWindow(self.root)
        
        # Setup menu
        self.setup_menu()

    def show_login(self) -> bool:
        """Display login window and return True if a user logged in."""
        self.root.withdraw()
        login_win = tk.Toplevel(self.root)
        login_app = LoginWindow(login_win)
        self.root.wait_window(login_win)
        self.root.deiconify()
        return get_current_user() is not None
        
    def setup_modern_theme(self):
        """Setup modern professional theme"""
        style = ttk.Style()
        
        # Use a modern theme as base
        try:
            style.theme_use('clam')
        except:
            try:
                style.theme_use('vista')
            except:
                style.theme_use('default')
        
        # Define modern color palette
        colors = {
            'primary': '#2c3e50',      # Dark blue-gray
            'secondary': '#3498db',     # Blue
            'success': '#27ae60',       # Green
            'warning': '#f39c12',       # Orange
            'danger': '#e74c3c',        # Red
            'light': '#ecf0f1',         # Light gray
            'dark': '#34495e',          # Dark gray
            'white': '#ffffff',
            'accent': '#9b59b6'         # Purple
        }
        
        # Configure modern styles
        
        # Headers and titles
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 18, 'bold'), 
                       foreground=colors['primary'])
        
        style.configure('Subtitle.TLabel', 
                       font=('Segoe UI', 10), 
                       foreground=colors['dark'])
        
        style.configure('PlaceholderTitle.TLabel', 
                       font=('Segoe UI', 16, 'bold'), 
                       foreground=colors['primary'])
        
        style.configure('PlaceholderText.TLabel', 
                       font=('Segoe UI', 10), 
                       foreground=colors['dark'],
                       justify='center')
        
        # Navigation styles
        style.configure('NavTitle.TLabel', 
                       font=('Segoe UI', 9, 'bold'), 
                       foreground=colors['dark'])
        
        # POS Button (special styling)
        style.configure('POS.TButton',
                       font=('Segoe UI', 11, 'bold'),
                       padding=(15, 12),
                       borderwidth=0)
        
        style.configure('POSActive.TButton',
                       font=('Segoe UI', 11, 'bold'),
                       padding=(15, 12),
                       borderwidth=2,
                       relief='solid')
        
        # Regular navigation buttons
        style.configure('Nav.TButton',
                       font=('Segoe UI', 10),
                       padding=(15, 10),
                       borderwidth=0)
        
        style.configure('NavActive.TButton',
                       font=('Segoe UI', 10, 'bold'),
                       padding=(15, 10),
                       borderwidth=2,
                       relief='solid')
        
        # Time and date
        style.configure('Time.TLabel', 
                       font=('Segoe UI', 14, 'bold'), 
                       foreground=colors['primary'])
        
        style.configure('Date.TLabel', 
                       font=('Segoe UI', 9), 
                       foreground=colors['dark'])
        
        # Stats labels
        style.configure('StatLabel.TLabel', 
                       font=('Segoe UI', 9), 
                       foreground=colors['dark'])
        
        style.configure('StatValue.TLabel', 
                       font=('Segoe UI', 10, 'bold'), 
                       foreground=colors['primary'])
        
        style.configure('StatAlert.TLabel', 
                       font=('Segoe UI', 10, 'bold'), 
                       foreground=colors['danger'])
        
        # Status bar
        style.configure('Status.TLabel', 
                       font=('Segoe UI', 9), 
                       foreground=colors['dark'])
        
        style.configure('Version.TLabel', 
                       font=('Segoe UI', 8), 
                       foreground=colors['dark'])
        
        # Frame styles
        style.configure('Header.TFrame', background=colors['light'])
        style.configure('Sidebar.TFrame', background='#f8f9fa')
        style.configure('Content.TFrame', background=colors['white'])
        style.configure('StatusBar.TFrame', background=colors['light'])
        style.configure('Panel.TFrame', background=colors['white'], relief='solid', borderwidth=1)
        
        # Modern LabelFrame
        style.configure('Modern.TLabelframe', 
                       background=colors['white'],
                       borderwidth=1,
                       relief='solid')
        style.configure('Modern.TLabelframe.Label', 
                       font=('Segoe UI', 10, 'bold'),
                       foreground=colors['primary'],
                       background=colors['white'])
        
        style.configure('Stats.TLabelframe', 
                       background='#f8f9fa',
                       borderwidth=1,
                       relief='solid')
        style.configure('Stats.TLabelframe.Label', 
                       font=('Segoe UI', 9, 'bold'),
                       foreground=colors['dark'],
                       background='#f8f9fa')
        
        # Form controls
        style.configure('FieldLabel.TLabel', 
                       font=('Segoe UI', 9, 'bold'), 
                       foreground=colors['dark'])
        
        style.configure('Modern.TEntry',
                       font=('Segoe UI', 10),
                       fieldbackground=colors['white'],
                       borderwidth=1,
                       relief='solid')
        
        style.configure('Modern.TCombobox',
                       font=('Segoe UI', 10),
                       fieldbackground=colors['white'])
        
        # Treeview modern styling
        style.configure('Modern.Treeview',
                       font=('Segoe UI', 9),
                       background=colors['white'],
                       fieldbackground=colors['white'],
                       borderwidth=1,
                       relief='solid')
        
        style.configure('Modern.Treeview.Heading',
                       font=('Segoe UI', 9, 'bold'),
                       background=colors['light'],
                       foreground=colors['primary'],
                       relief='flat')
        
        # POS specific button styles
        style.configure('AddCart.TButton',
                       font=('Segoe UI', 10, 'bold'),
                       padding=(20, 8))
        
        style.configure('CartAction.TButton',
                       font=('Segoe UI', 9),
                       padding=(8, 4))
        
        style.configure('ProcessSale.TButton',
                       font=('Segoe UI', 12, 'bold'),
                       padding=(20, 15))
        
        style.configure('Secondary.TButton',
                       font=('Segoe UI', 9),
                       padding=(10, 8))
        
        # Total labels styling
        style.configure('TotalLabel.TLabel', 
                       font=('Segoe UI', 10), 
                       foreground=colors['dark'])
        
        style.configure('TotalValue.TLabel', 
                       font=('Segoe UI', 11, 'bold'), 
                       foreground=colors['primary'])
        
        style.configure('GrandTotal.TLabel', 
                       font=('Segoe UI', 14, 'bold'), 
                       foreground=colors['success'])
        
        style.configure('ChangeValue.TLabel', 
                       font=('Segoe UI', 12, 'bold'), 
                       foreground=colors['success'])
    
    def init_database(self):
        """Initialize database and add sample data if needed"""
        try:
            init_database()
            self.add_sample_data()
            print("Database initialized successfully!")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to initialize database: {e}")
            print(f"Database error: {e}")
    
    def add_sample_data(self):
        """Add enhanced sample data for testing"""
        session = db_manager.get_session()
        try:
            from database.models import Category, Product, Customer
            
            # Check if we already have data
            if session.query(Category).count() > 0:
                return
            
            # Add categories with better organization
            categories_data = [
                {"name": "Cement & Concrete", "description": "Portland cement, ready-mix concrete, concrete additives"},
                {"name": "Steel & Iron", "description": "Rebar, steel sheets, iron rods, structural steel"},
                {"name": "Bricks & Blocks", "description": "Building bricks, concrete blocks, clay bricks"},
                {"name": "Roofing Materials", "description": "Metal sheets, tiles, gutters, roof accessories"},
                {"name": "Plumbing Supplies", "description": "Pipes, fittings, valves, bathroom fixtures"},
                {"name": "Electrical Items", "description": "Cables, switches, outlets, electrical accessories"},
                {"name": "Tools & Hardware", "description": "Hand tools, power tools, fasteners, hardware"},
                {"name": "Paint & Finishes", "description": "Paints, primers, brushes, finishing materials"},
                {"name": "Doors & Windows", "description": "Doors, windows, frames, glass, locks"},
                {"name": "Insulation & Drywall", "description": "Insulation materials, drywall, joint compounds"}
            ]
            
            categories = []
            for cat_data in categories_data:
                category = Category(**cat_data)
                session.add(category)
                categories.append(category)
            
            session.flush()  # Get IDs
            
            # Add comprehensive sample products
            products_data = [
                # Cement & Concrete
                {"name": "Portland Cement 50kg", "category_id": categories[0].id, "unit": "bag", 
                 "cost_price": 4500, "selling_price": 5500, "stock_quantity": 150, "barcode": "CEM001"},
                {"name": "Ready Mix Concrete M25", "category_id": categories[0].id, "unit": "m3", 
                 "cost_price": 85000, "selling_price": 95000, "stock_quantity": 25, "barcode": "CON001"},
                {"name": "Concrete Admixture", "category_id": categories[0].id, "unit": "liter", 
                 "cost_price": 1200, "selling_price": 1500, "stock_quantity": 50, "barcode": "ADM001"},
                
                # Steel & Iron
                {"name": "Steel Rebar 12mm x 12m", "category_id": categories[1].id, "unit": "piece", 
                 "cost_price": 8500, "selling_price": 9500, "stock_quantity": 200, "barcode": "STL001"},
                {"name": "Iron Sheet 26 Gauge", "category_id": categories[1].id, "unit": "sheet", 
                 "cost_price": 15000, "selling_price": 17000, "stock_quantity": 75, "barcode": "IRN001"},
                {"name": "Steel Angle 40x40x5mm", "category_id": categories[1].id, "unit": "meter", 
                 "cost_price": 850, "selling_price": 1000, "stock_quantity": 100, "barcode": "ANG001"},
                
                # Bricks & Blocks
                {"name": "Red Building Brick", "category_id": categories[2].id, "unit": "piece", 
                 "cost_price": 180, "selling_price": 220, "stock_quantity": 5000, "barcode": "BRK001"},
                {"name": "Concrete Block 8inch", "category_id": categories[2].id, "unit": "piece", 
                 "cost_price": 450, "selling_price": 550, "stock_quantity": 800, "barcode": "BLK001"},
                {"name": "Hollow Block 6inch", "category_id": categories[2].id, "unit": "piece", 
                 "cost_price": 350, "selling_price": 450, "stock_quantity": 600, "barcode": "HOL001"},
                
                # Roofing
                {"name": "Aluminum Roofing Sheet 3m", "category_id": categories[3].id, "unit": "sheet", 
                 "cost_price": 12000, "selling_price": 14000, "stock_quantity": 120, "barcode": "ALU001"},
                {"name": "Clay Roof Tiles", "category_id": categories[3].id, "unit": "piece", 
                 "cost_price": 450, "selling_price": 550, "stock_quantity": 2000, "barcode": "TIL001"},
                {"name": "Rain Gutter 4inch", "category_id": categories[3].id, "unit": "meter", 
                 "cost_price": 1200, "selling_price": 1500, "stock_quantity": 80, "barcode": "GUT001"},
                
                # Plumbing
                {"name": "PVC Pipe 4inch x 6m", "category_id": categories[4].id, "unit": "piece", 
                 "cost_price": 5100, "selling_price": 6000, "stock_quantity": 150, "barcode": "PVC001"},
                {"name": "PVC Elbow 4inch", "category_id": categories[4].id, "unit": "piece", 
                 "cost_price": 350, "selling_price": 450, "stock_quantity": 200, "barcode": "ELB001"},
                {"name": "Water Faucet Standard", "category_id": categories[4].id, "unit": "piece", 
                 "cost_price": 2500, "selling_price": 3200, "stock_quantity": 45, "barcode": "FAU001"},
                
                # Electrical
                {"name": "Electrical Cable 2.5mm", "category_id": categories[5].id, "unit": "meter", 
                 "cost_price": 180, "selling_price": 250, "stock_quantity": 500, "barcode": "CAB001"},
                {"name": "Wall Switch Double", "category_id": categories[5].id, "unit": "piece", 
                 "cost_price": 850, "selling_price": 1100, "stock_quantity": 80, "barcode": "SWI001"},
                {"name": "Power Outlet 13A", "category_id": categories[5].id, "unit": "piece", 
                 "cost_price": 650, "selling_price": 850, "stock_quantity": 60, "barcode": "OUT001"},
                
                # Tools
                {"name": "Claw Hammer 500g", "category_id": categories[6].id, "unit": "piece", 
                 "cost_price": 2500, "selling_price": 3200, "stock_quantity": 25, "barcode": "HAM001"},
                {"name": "Screwdriver Set (6pc)", "category_id": categories[6].id, "unit": "set", 
                 "cost_price": 1800, "selling_price": 2500, "stock_quantity": 15, "barcode": "SCR001"},
                {"name": "Measuring Tape 5m", "category_id": categories[6].id, "unit": "piece", 
                 "cost_price": 1200, "selling_price": 1600, "stock_quantity": 30, "barcode": "TAP001"},
                
                # Paint
                {"name": "Exterior Paint 4L White", "category_id": categories[7].id, "unit": "bucket", 
                 "cost_price": 8500, "selling_price": 10500, "stock_quantity": 40, "barcode": "PAI001"},
                {"name": "Paint Brush 3inch", "category_id": categories[7].id, "unit": "piece", 
                 "cost_price": 450, "selling_price": 650, "stock_quantity": 35, "barcode": "BRU001"},
                {"name": "Paint Roller Kit", "category_id": categories[7].id, "unit": "set", 
                 "cost_price": 1500, "selling_price": 2000, "stock_quantity": 20, "barcode": "ROL001"},
                
                # Doors & Windows
                {"name": "Interior Door 80x200cm", "category_id": categories[8].id, "unit": "piece", 
                 "cost_price": 45000, "selling_price": 55000, "stock_quantity": 12, "barcode": "DOR001"},
                {"name": "Window Frame Aluminum", "category_id": categories[8].id, "unit": "piece", 
                 "cost_price": 25000, "selling_price": 32000, "stock_quantity": 8, "barcode": "WIN001"},
                
                # Insulation
                {"name": "Fiberglass Insulation Roll", "category_id": categories[9].id, "unit": "roll", 
                 "cost_price": 12000, "selling_price": 15000, "stock_quantity": 30, "barcode": "INS001"},
                {"name": "Drywall Sheet 4x8ft", "category_id": categories[9].id, "unit": "sheet", 
                 "cost_price": 3500, "selling_price": 4200, "stock_quantity": 50, "barcode": "DRY001"}
            ]
            
            for prod_data in products_data:
                product = Product(**prod_data)
                session.add(product)
            
            # Add default customer with better info
            default_customer = Customer(
                name="Walk-in Customer",
                phone="N/A",
                email="",
                address="Cash Customer",
                credit_limit=0
            )
            session.add(default_customer)
            
            session.commit()
            print("Enhanced sample data added successfully!")
            
        except Exception as e:
            session.rollback()
            print(f"Error adding sample data: {e}")
        finally:
            if session:
                session.close()
    
    def setup_menu(self):
        """Setup modern application menu bar"""
        menubar = tk.Menu(self.root, font=('Segoe UI', 9))
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, font=('Segoe UI', 9))
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="🔄 Backup Database", command=self.backup_database)
        file_menu.add_command(label="📊 Export Data", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="🚪 Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, font=('Segoe UI', 9))
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="💳 Point of Sale", command=lambda: self.main_window.show_pos())
        view_menu.add_command(label="📦 Inventory", command=lambda: self.main_window.show_inventory())
        view_menu.add_command(label="📊 Reports", command=lambda: self.main_window.show_reports())
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, font=('Segoe UI', 9))
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="📖 User Guide", command=self.show_user_guide)
        help_menu.add_command(label="🆘 Support", command=self.show_support)
        help_menu.add_separator()
        help_menu.add_command(label="ℹ️ About", command=self.show_about)
        
    def backup_database(self):
        """Create database backup"""
        try:
            backup_path = db_manager.backup_database()
            messagebox.showinfo("✅ Backup Complete", 
                              f"Database successfully backed up to:\n{backup_path}")
        except Exception as e:
            messagebox.showerror("❌ Backup Error", f"Failed to backup database:\n{e}")
    
    def export_data(self):
        """Export data functionality"""
        messagebox.showinfo("📊 Export Data", 
                          "Data export functionality available in Reports section.\n"
                          "Use Reports → Export to CSV for detailed data export.")
    
    def show_user_guide(self):
        """Show user guide"""
        guide_text = """
🏗️ CONSTRUCTION POS - USER GUIDE

QUICK START:
1️⃣ Click 'Point of Sale' to process transactions
2️⃣ Search for products and add to cart
3️⃣ Select customer and payment method
4️⃣ Complete sale and generate receipt

INVENTORY MANAGEMENT:
• Add/edit products and categories
• Monitor stock levels and alerts
• Adjust inventory quantities
• Track product performance

REPORTS & ANALYTICS:
• View daily/monthly sales reports
• Monitor inventory valuation
• Track top-selling products
• Export data to CSV files

TIPS:
• Double-click products to add to cart
• Use search to quickly find items
• Monitor low stock alerts regularly
• Keep regular database backups
        """
        
        # Create a scrollable text window
        guide_window = tk.Toplevel(self.root)
        guide_window.title("📖 User Guide")
        guide_window.geometry("600x500")
        guide_window.transient(self.root)
        
        text_widget = tk.Text(guide_window, wrap=tk.WORD, font=('Segoe UI', 10), padx=20, pady=20)
        scrollbar = ttk.Scrollbar(guide_window, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget.insert(tk.END, guide_text)
        text_widget.config(state=tk.DISABLED)
    
    def show_support(self):
        """Show support information"""
        support_text = """
🆘 TECHNICAL SUPPORT

TROUBLESHOOTING:
• Restart the application if issues occur
• Check that you have write permissions
• Ensure adequate disk space (>100MB)
• Keep regular backups of your database

COMMON SOLUTIONS:
• Database errors: Run as administrator
• Slow performance: Close other applications
• Missing products: Check Inventory section

BACKUP IMPORTANT:
Your data is stored in 'construction_pos.db'
Keep regular backups via File → Backup Database

SYSTEM INFO:
• Offline operation - no internet required
• All data stored locally on this computer
• Compatible with Windows 7/8/10/11
• Automatic data persistence
        """
        messagebox.showinfo("🆘 Support", support_text)
    
    def show_about(self):
        """Show modern about dialog"""
        about_text = """
🏗️ Construction Materials POS System
Version 1.0.0

A professional Point of Sale system designed specifically 
for construction material shops and hardware stores.

✨ KEY FEATURES:
• Complete offline operation
• Comprehensive inventory management
• Professional sales processing
• Detailed reporting and analytics
• Customer management
• Automatic data backup

🛠️ TECHNICAL DETAILS:
• Built with Python & Tkinter
• SQLite database for reliability
• Modern user interface
• Cross-platform compatibility

💼 PERFECT FOR:
• Construction material shops
• Hardware stores
• Building supply companies
• Tool and equipment retailers

🚀 No internet connection required
📊 Professional-grade business solution
        """
        
        # Create attractive about dialog
        about_window = tk.Toplevel(self.root)
        about_window.title("About Construction POS")
        about_window.geometry("500x450")
        about_window.transient(self.root)
        about_window.resizable(False, False)
        
        # Center the window
        about_window.geometry("500x450+{}+{}".format(
            self.root.winfo_rootx() + 100,
            self.root.winfo_rooty() + 50
        ))
        
        # Main frame
        main_frame = ttk.Frame(about_window, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # About text
        text_widget = tk.Text(main_frame, wrap=tk.WORD, font=('Segoe UI', 10), 
                             height=20, borderwidth=0, relief='flat')
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, about_text)
        text_widget.config(state=tk.DISABLED)
        
        # OK button
        ttk.Button(main_frame, text="OK", command=about_window.destroy, 
                  style='Secondary.TButton').pack(pady=(20, 0))
    
    def run(self):
        """Start the application"""
        if self.root is None:
            return
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("Application stopped by user")
        except Exception as e:
            messagebox.showerror("Application Error", f"An error occurred: {e}")

if __name__ == "__main__":
    try:
        app = ConstructionPOSApp()
        app.run()
    except Exception as e:
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Startup Error", f"Failed to start application: {e}")
        except:
            print(f"Critical error: {e}")
        sys.exit(1)
