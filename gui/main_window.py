import tkinter as tk
from tkinter import ttk
from datetime import datetime
from database.database import DatabaseUtils
from utils.i18n import translate as _
from .pos_window import POSWindow
from .inventory_window import InventoryWindow
from .reports_window import ReportsWindow
from .customers_window import CustomersWindow
from .settings_window import SettingsWindow

class MainWindow:
    """Main application window with navigation."""
    def __init__(self, root):
        self.root = root
        self.current_window = None

        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

        self.setup_ui()
        self.show_pos()

    def setup_ui(self):
        self.create_header()
        self.create_sidebar()
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)
        self.create_status_bar()

    def create_header(self):
        header = ttk.Frame(self.main_frame)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        header.columnconfigure(1, weight=1)
        app_name = DatabaseUtils.get_setting_value('shop_name', 'Quincaillerie Fexson')
        ttk.Label(header, text=app_name, style='Title.TLabel').grid(row=0, column=0, sticky="w")
        self.time_label = ttk.Label(header, text="", font=('Arial', 10))
        self.time_label.grid(row=0, column=2, sticky="e")
        self.update_time()

    def update_time(self):
        self.time_label.config(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.root.after(1000, self.update_time)

    def create_sidebar(self):
        sidebar = ttk.LabelFrame(self.main_frame, text="Navigation", padding="10")
        sidebar.grid(row=1, column=0, sticky="ns")
        buttons = [
            (f"🛒 { _('pos') }", self.show_pos),
            (f"📦 { _('inventory') }", self.show_inventory),
            (f"📊 { _('reports') }", self.show_reports),
            (f"👥 { _('customers') }", self.show_customers),
            (f"⚙️ { _('settings') }", self.show_settings),
        ]
        for i, (text, cmd) in enumerate(buttons):
            ttk.Button(sidebar, text=text, command=cmd, style='Large.TButton', width=15).grid(row=i, column=0, pady=5, sticky="ew")

    def create_status_bar(self):
        self.status_label = ttk.Label(self.main_frame, text="Ready", relief=tk.SUNKEN)
        self.status_label.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def update_status(self, message):
        self.status_label.config(text=message)

    def show_pos(self):
        self.clear_content()
        self.current_window = POSWindow(self.content_frame)
        self.update_status("Point of Sale - Ready")

    def show_inventory(self):
        self.clear_content()
        self.current_window = InventoryWindow(self.content_frame)
        self.update_status("Inventory Management")

    def show_reports(self):
        self.clear_content()
        self.current_window = ReportsWindow(self.content_frame)
        self.update_status("Reports & Analytics")

    def show_customers(self):
        self.clear_content()
        self.current_window = CustomersWindow(self.content_frame)
        self.update_status("Customers")

    def show_settings(self):
        self.clear_content()
        self.current_window = SettingsWindow(self.content_frame, self.root)
        self.update_status(_("settings"))
