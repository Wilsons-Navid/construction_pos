import tkinter as tk
from tkinter import ttk, messagebox
from database.database import db_manager, DatabaseUtils
from database.models import User
from utils.auth import hash_password
from utils.i18n import translate as _


class SettingsWindow:
    """Settings window for user management and preferences."""

    def __init__(self, parent, root):
        self.parent = parent
        self.root = root
        self.setup_ui()

    def setup_ui(self):
        notebook = ttk.Notebook(self.parent)
        notebook.pack(fill="both", expand=True)

        # Users tab
        user_frame = ttk.Frame(notebook, padding=10)
        notebook.add(user_frame, text=_('users'))

        ttk.Label(user_frame, text=_('username')).grid(row=0, column=0, sticky=tk.W)
        self.username_var = tk.StringVar()
        ttk.Entry(user_frame, textvariable=self.username_var).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(user_frame, text=_('password')).grid(row=1, column=0, sticky=tk.W)
        self.password_var = tk.StringVar()
        ttk.Entry(user_frame, textvariable=self.password_var, show='*').grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

        ttk.Button(user_frame, text=_('add_user'), command=self.add_user).grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))

        self.users_tree = ttk.Treeview(user_frame, columns=('id', 'username'), show='headings', height=5)
        self.users_tree.heading('id', text=_('id'))
        self.users_tree.heading('username', text=_('username'))
        self.users_tree.column('id', width=50, anchor='center')
        self.users_tree.column('username', width=150, anchor='w')
        self.users_tree.grid(row=3, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        user_frame.columnconfigure(1, weight=1)
        self.load_users()

        # Preferences tab
        pref_frame = ttk.Frame(notebook, padding=10)
        notebook.add(pref_frame, text=_('preferences'))

        ttk.Label(pref_frame, text=_('language')).grid(row=0, column=0, sticky=tk.W)
        self.lang_var = tk.StringVar(value=DatabaseUtils.get_setting_value('language', 'en'))
        lang_combo = ttk.Combobox(pref_frame, textvariable=self.lang_var, values=['en', 'fr'], state='readonly')
        lang_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(pref_frame, text=_('theme')).grid(row=1, column=0, sticky=tk.W)
        self.theme_var = tk.StringVar(value=DatabaseUtils.get_setting_value('theme', 'light'))
        theme_combo = ttk.Combobox(pref_frame, textvariable=self.theme_var, values=['light', 'dark'], state='readonly')
        theme_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

        ttk.Button(pref_frame, text=_('save_preferences'), command=self.save_preferences).grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        pref_frame.columnconfigure(1, weight=1)

    def add_user(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()
        if not username or not password:
            messagebox.showerror(_('settings'), _('credentials_required'))
            return
        session = db_manager.get_session()
        try:
            if session.query(User).filter(User.username == username).first():
                messagebox.showerror(_('settings'), _('username_exists'))
                return
            user = User(username=username, password_hash=hash_password(password))
            session.add(user)
            session.commit()
            messagebox.showinfo(_('settings'), _('user_added'))
            self.username_var.set('')
            self.password_var.set('')
            self.load_users()
        finally:
            session.close()

    def load_users(self):
        session = db_manager.get_session()
        try:
            for item in self.users_tree.get_children():
                self.users_tree.delete(item)
            users = session.query(User).all()
            for user in users:
                self.users_tree.insert('', tk.END, values=(user.id, user.username))
        finally:
            session.close()

    def save_preferences(self):
        DatabaseUtils.update_setting('language', self.lang_var.get())
        DatabaseUtils.update_setting('theme', self.theme_var.get())

        messagebox.showinfo(_('settings'), _('preferences_saved'))
        # Notify root to reapply theme and language if possible

        try:
            from .main_window import MainWindow  # avoid circular if possible
            style = ttk.Style()
            if self.theme_var.get() == 'dark':
                style.theme_use('alt')
                self.root.configure(background='#2c3e50')
            else:
                style.theme_use('clam')
                self.root.configure(background='white')
        except Exception:
            pass

        try:
            self.root.event_generate('<<LanguageChanged>>', when='tail')
        except Exception:
            messagebox.showinfo(_('settings'), _('language_changed'))


