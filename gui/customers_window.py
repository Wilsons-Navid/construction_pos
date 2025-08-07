import tkinter as tk
from tkinter import ttk
from database.database import db_manager
from database.models import Customer, Sale, SaleItem
from utils.i18n import translate as _

class CustomersWindow:
    """Display customers and their purchase history."""
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        self.load_customers()

    def setup_ui(self):
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)

        main_pane = ttk.PanedWindow(self.parent, orient=tk.HORIZONTAL)
        main_pane.grid(row=0, column=0, sticky="nsew")

        # Customers list
        left_frame = ttk.Frame(main_pane)
        main_pane.add(left_frame, weight=1)

        self.customers_tree = ttk.Treeview(left_frame, columns=("ID", "Name"), show="headings", height=15)
        self.customers_tree.heading("ID", text=_('id'))
        self.customers_tree.heading("Name", text=_('customer_label'))
        self.customers_tree.column("ID", width=50, anchor="center")
        self.customers_tree.column("Name", width=150)
        self.customers_tree.pack(fill="both", expand=True)
        self.customers_tree.bind("<<TreeviewSelect>>", self.on_customer_select)

        # Sales and items
        right_frame = ttk.Frame(main_pane)
        main_pane.add(right_frame, weight=2)
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)

        self.sales_tree = ttk.Treeview(right_frame, columns=("Sale", "Date", "Total"), show="headings", height=8)
        self.sales_tree.heading("Sale", text=_('sale_number'))
        self.sales_tree.heading("Date", text=_('date'))
        self.sales_tree.heading("Total", text=_('total_label'))
        self.sales_tree.column("Sale", width=100, anchor="center")
        self.sales_tree.column("Date", width=140, anchor="center")
        self.sales_tree.column("Total", width=100, anchor="e")
        self.sales_tree.grid(row=0, column=0, sticky="ew")
        self.sales_tree.bind("<<TreeviewSelect>>", self.on_sale_select)

        self.items_tree = ttk.Treeview(right_frame, columns=("Product", "Qty", "Amount"), show="headings")
        self.items_tree.heading("Product", text=_('shopping_cart_product'))
        self.items_tree.heading("Qty", text=_('qty'))
        self.items_tree.heading("Amount", text=_('amount'))
        self.items_tree.column("Product", width=200)
        self.items_tree.column("Qty", width=60, anchor="center")
        self.items_tree.column("Amount", width=100, anchor="e")
        self.items_tree.grid(row=1, column=0, sticky="nsew")

    def load_customers(self):
        session = db_manager.get_session()
        try:
            customers = session.query(Customer).order_by(Customer.id).all()
            for cust in customers:
                self.customers_tree.insert("", tk.END, iid=cust.id, values=(cust.id, cust.name))
        finally:
            session.close()

    def on_customer_select(self, event):
        sel = self.customers_tree.focus()
        if not sel:
            return
        customer_id = int(sel)
        session = db_manager.get_session()
        try:
            sales = session.query(Sale).filter(Sale.customer_id == customer_id).order_by(Sale.created_at.desc()).all()
            for item in self.sales_tree.get_children():
                self.sales_tree.delete(item)
            for s in sales:
                self.sales_tree.insert("", tk.END, iid=s.id, values=(s.sale_number, s.created_at.strftime("%Y-%m-%d %H:%M"), f"{s.total_amount:,.0f}"))
            for item in self.items_tree.get_children():
                self.items_tree.delete(item)
        finally:
            session.close()

    def on_sale_select(self, event):
        sel = self.sales_tree.focus()
        if not sel:
            return
        sale_id = int(sel)
        session = db_manager.get_session()
        try:
            items = session.query(SaleItem).filter(SaleItem.sale_id == sale_id).all()
            for item in self.items_tree.get_children():
                self.items_tree.delete(item)
            for it in items:
                product_name = it.product.name if it.product else str(it.product_id)
                self.items_tree.insert("", tk.END, values=(product_name, it.quantity, f"{it.total_price:,.0f}"))
        finally:
            session.close()
