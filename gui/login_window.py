"""Login window for the POS system."""

import tkinter as tk
from tkinter import ttk, messagebox

from database.database import db_manager
from database.models import User
from utils.auth import verify_password, set_current_user


class LoginWindow:
    """Simple modal login window."""

    def __init__(self, root: tk.Toplevel):
        self.root = root
        self.root.title("User Login")
        self.root.geometry("300x160")
        self.user = None

        frame = ttk.Frame(root, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Username:").grid(row=0, column=0, sticky=tk.W)
        self.username_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.username_var).grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Password:").grid(row=1, column=0, sticky=tk.W)
        self.password_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.password_var, show="*").grid(row=1, column=1, pady=5)

        login_btn = ttk.Button(frame, text="Login", command=self.login)
        login_btn.grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))

        self.root.bind("<Return>", lambda _e: self.login())

    def login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()

        session = db_manager.get_session()
        try:
            user = (
                session.query(User)
                .filter(User.username == username, User.is_active == True)
                .first()
            )
            if user and verify_password(password, user.password_hash):
                set_current_user(user)
                self.user = user
                self.root.destroy()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password")
        finally:
            session.close()

