import tkinter as tk
from tkinter import ttk, messagebox
from database.database import db_manager, DatabaseUtils
from database.models import User
from utils.auth import hash_password, get_current_user, verify_password
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

        buttons_frame = ttk.Frame(user_frame)
        buttons_frame.grid(row=4, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(buttons_frame, text=_('edit_user'), command=self.edit_user).pack(side=tk.LEFT, expand=True, fill='x', padx=2)
        ttk.Button(buttons_frame, text=_('delete_user'), command=self.delete_user).pack(side=tk.LEFT, expand=True, fill='x', padx=2)
        ttk.Button(buttons_frame, text=_('change_password'), command=self.change_password).pack(side=tk.LEFT, expand=True, fill='x', padx=2)

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

    def get_selected_user_id(self):
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning(_('settings'), _('select_user'))
            return None
        return self.users_tree.item(selection[0])['values'][0]

    def edit_user(self):
        user_id = self.get_selected_user_id()
        if user_id is None:
            return
        session = db_manager.get_session()
        try:
            user = session.query(User).get(user_id)
        finally:
            session.close()
        if not user:
            return

        dialog = tk.Toplevel(self.parent)
        dialog.title(_('edit_user'))
        dialog.transient(self.parent)
        dialog.grab_set()

        username_var = tk.StringVar(value=user.username)
        ttk.Label(dialog, text=_('username')).grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        ttk.Entry(dialog, textvariable=username_var).grid(row=0, column=1, padx=10, pady=10)

        def save():
            new_username = username_var.get().strip()
            if not new_username:
                messagebox.showerror(_('settings'), _('credentials_required'))
                return
            session2 = db_manager.get_session()
            try:
                if session2.query(User).filter(User.username == new_username, User.id != user_id).first():
                    messagebox.showerror(_('settings'), _('username_exists'))
                    return
                user_obj = session2.query(User).get(user_id)
                user_obj.username = new_username
                session2.commit()
                messagebox.showinfo(_('settings'), _('user_updated'))
                self.load_users()
                dialog.destroy()
            finally:
                session2.close()

        ttk.Button(dialog, text='Save', command=save).grid(row=1, column=0, columnspan=2, pady=10)

    def delete_user(self):
        user_id = self.get_selected_user_id()
        if user_id is None:
            return
        current = get_current_user()
        if current and current.id == user_id:
            messagebox.showwarning(_('settings'), _('cannot_delete_current_user'))
            return
        if not messagebox.askyesno(_('settings'), _('confirm_delete_user')):
            return
        session = db_manager.get_session()
        try:
            user = session.query(User).get(user_id)
            if user:
                session.delete(user)
                session.commit()
                messagebox.showinfo(_('settings'), _('user_deleted'))
                self.load_users()
        finally:
            session.close()

    def change_password(self):
        user_id = self.get_selected_user_id()
        if user_id is None:
            return
        current = get_current_user()

        dialog = tk.Toplevel(self.parent)
        dialog.title(_('change_password'))
        dialog.transient(self.parent)
        dialog.grab_set()

        row = 0
        old_pass_var = None
        if current and current.id == user_id:
            old_pass_var = tk.StringVar()
            ttk.Label(dialog, text=_('old_password')).grid(row=row, column=0, padx=10, pady=5, sticky=tk.W)
            ttk.Entry(dialog, textvariable=old_pass_var, show='*').grid(row=row, column=1, padx=10, pady=5)
            row += 1

        new_pass_var = tk.StringVar()
        ttk.Label(dialog, text=_('new_password')).grid(row=row, column=0, padx=10, pady=5, sticky=tk.W)
        ttk.Entry(dialog, textvariable=new_pass_var, show='*').grid(row=row, column=1, padx=10, pady=5)
        row += 1

        confirm_var = tk.StringVar()
        ttk.Label(dialog, text=_('confirm_password')).grid(row=row, column=0, padx=10, pady=5, sticky=tk.W)
        ttk.Entry(dialog, textvariable=confirm_var, show='*').grid(row=row, column=1, padx=10, pady=5)
        row += 1

        def save_pwd():
            new_pass = new_pass_var.get()
            if new_pass != confirm_var.get() or not new_pass:
                messagebox.showerror(_('settings'), _('password_mismatch'))
                return
            session2 = db_manager.get_session()
            try:
                user_obj = session2.query(User).get(user_id)
                if old_pass_var is not None:
                    if not verify_password(old_pass_var.get(), user_obj.password_hash):
                        messagebox.showerror(_('settings'), _('password_incorrect'))
                        return
                user_obj.password_hash = hash_password(new_pass)
                session2.commit()
                messagebox.showinfo(_('settings'), _('password_changed'))
                dialog.destroy()
            finally:
                session2.close()

        ttk.Button(dialog, text='Save', command=save_pwd).grid(row=row, column=0, columnspan=2, pady=10)

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


