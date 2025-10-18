"""
ui.py - Giao diện người dùng cho Password Manager

Sử dụng tkinter để tạo GUI đơn giản và rõ ràng
Bao gồm:
- Màn hình đăng nhập
- Màn hình chính với danh sách mật khẩu
- Dialog thêm/sửa entry
- Tự động khóa sau thời gian không hoạt động
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
from typing import Optional, Callable
from app.vault import Vault, VaultEntry
from app.utils import generate_password, copy_to_clipboard_temporary, validate_master_password, validate_entry_data


class PasswordManagerUI:
    """Giao diện chính của Password Manager"""
    
    def __init__(self, vault: Vault):
        self.vault = vault
        self.root = tk.Tk()
        self.root.title("Password Manager")
        self.root.geometry("800x600")
        
        # Timer cho tự động khóa (2 phút = 120 giây)
        self.auto_lock_time = 120
        self.last_activity = None
        self.auto_lock_timer = None
        
        # Frame hiện tại
        self.current_frame = None
        
        # Bind sự kiện đóng cửa sổ
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Khởi động với màn hình login
        self.show_login_screen()
    
    def run(self):
        """Chạy ứng dụng"""
        self.root.mainloop()
    
    def on_closing(self):
        """Xử lý khi đóng ứng dụng"""
        if self.vault.is_unlocked:
            if messagebox.askokcancel("Thoát", "Bạn có muốn lưu và thoát?"):
                self.vault.save()
                self.vault.lock()
                self.root.destroy()
        else:
            self.root.destroy()
    
    def reset_activity_timer(self):
        """Reset timer tự động khóa khi có hoạt động"""
        import time
        self.last_activity = time.time()
        
        # Hủy timer cũ và tạo timer mới
        if self.auto_lock_timer:
            self.auto_lock_timer.cancel()
        
        if self.vault.is_unlocked:
            self.auto_lock_timer = threading.Timer(self.auto_lock_time, self.auto_lock)
            self.auto_lock_timer.daemon = True
            self.auto_lock_timer.start()
    
    def auto_lock(self):
        """Tự động khóa vault sau thời gian không hoạt động"""
        if self.vault.is_unlocked:
            self.vault.lock()
            messagebox.showinfo("Tự động khóa", "Vault đã bị khóa do không hoạt động")
            self.show_login_screen()
    
    def clear_frame(self):
        """Xóa frame hiện tại"""
        if self.current_frame:
            self.current_frame.destroy()
    
    def show_login_screen(self):
        """Hiển thị màn hình đăng nhập"""
        self.clear_frame()
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(expand=True, fill='both')
        
        # Title
        title = tk.Label(self.current_frame, text="Password Manager", 
                        font=("Arial", 24, "bold"))
        title.pack(pady=30)
        
        # Kiểm tra xem vault đã tồn tại chưa
        vault_exists = self.vault.vault_exists()
        
        if vault_exists:
            subtitle = tk.Label(self.current_frame, text="Nhập master password để mở vault", 
                              font=("Arial", 12))
        else:
            subtitle = tk.Label(self.current_frame, text="Tạo vault mới - Nhập master password", 
                              font=("Arial", 12))
        subtitle.pack(pady=10)
        
        # Password frame
        password_frame = tk.Frame(self.current_frame)
        password_frame.pack(pady=20)
        
        tk.Label(password_frame, text="Master Password:", font=("Arial", 11)).grid(row=0, column=0, padx=10, pady=10)
        password_entry = tk.Entry(password_frame, show="*", width=30, font=("Arial", 11))
        password_entry.grid(row=0, column=1, padx=10, pady=10)
        password_entry.focus()
        
        # Confirm password (chỉ khi tạo mới)
        confirm_entry = None
        if not vault_exists:
            tk.Label(password_frame, text="Xác nhận Password:", font=("Arial", 11)).grid(row=1, column=0, padx=10, pady=10)
            confirm_entry = tk.Entry(password_frame, show="*", width=30, font=("Arial", 11))
            confirm_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # Buttons
        button_frame = tk.Frame(self.current_frame)
        button_frame.pack(pady=20)
        
        def on_submit():
            password = password_entry.get()
            
            if not vault_exists:
                # Tạo vault mới
                confirm = confirm_entry.get() if confirm_entry else ""
                
                if password != confirm:
                    messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp")
                    return
                
                # Validate master password
                is_valid, error_msg = validate_master_password(password)
                if not is_valid:
                    messagebox.showerror("Lỗi", error_msg)
                    return
                
                if self.vault.create_new_vault(password):
                    messagebox.showinfo("Thành công", "Vault đã được tạo thành công!")
                    self.show_main_screen()
                else:
                    messagebox.showerror("Lỗi", "Không thể tạo vault")
            else:
                # Mở vault hiện có
                if self.vault.unlock(password):
                    self.show_main_screen()
                else:
                    messagebox.showerror("Lỗi", "Sai master password hoặc vault bị lỗi")
        
        # Bind Enter key
        password_entry.bind('<Return>', lambda e: on_submit())
        if confirm_entry:
            confirm_entry.bind('<Return>', lambda e: on_submit())
        
        if vault_exists:
            submit_btn = tk.Button(button_frame, text="Mở Vault", command=on_submit, 
                                  font=("Arial", 11), width=15, bg="#4CAF50", fg="white")
        else:
            submit_btn = tk.Button(button_frame, text="Tạo Vault", command=on_submit, 
                                  font=("Arial", 11), width=15, bg="#2196F3", fg="white")
        submit_btn.pack()
    
    def show_main_screen(self):
        """Hiển thị màn hình chính với danh sách mật khẩu"""
        self.clear_frame()
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Reset activity timer
        self.reset_activity_timer()
        
        # Title
        title_frame = tk.Frame(self.current_frame)
        title_frame.pack(fill='x', pady=5)
        
        tk.Label(title_frame, text="Danh sách mật khẩu", 
                font=("Arial", 16, "bold")).pack(side='left')
        
        # Lock button
        lock_btn = tk.Button(title_frame, text="🔒 Khóa", command=self.lock_vault, 
                           font=("Arial", 10), bg="#f44336", fg="white")
        lock_btn.pack(side='right', padx=5)
        
        # Toolbar
        toolbar = tk.Frame(self.current_frame)
        toolbar.pack(fill='x', pady=10)
        
        tk.Button(toolbar, text="➕ Thêm", command=self.add_entry, 
                 font=("Arial", 10), bg="#4CAF50", fg="white", width=12).pack(side='left', padx=5)
        tk.Button(toolbar, text="✏️ Sửa", command=self.edit_entry, 
                 font=("Arial", 10), bg="#2196F3", fg="white", width=12).pack(side='left', padx=5)
        tk.Button(toolbar, text="🗑️ Xóa", command=self.delete_entry, 
                 font=("Arial", 10), bg="#f44336", fg="white", width=12).pack(side='left', padx=5)
        tk.Button(toolbar, text="📋 Copy Password", command=self.copy_password, 
                 font=("Arial", 10), bg="#FF9800", fg="white", width=15).pack(side='left', padx=5)
        tk.Button(toolbar, text="🔑 Sinh Password", command=self.show_password_generator, 
                 font=("Arial", 10), bg="#9C27B0", fg="white", width=15).pack(side='left', padx=5)
        tk.Button(toolbar, text="🛡️ Đổi Master", command=self.show_change_master_dialog, 
                 font=("Arial", 10), bg="#607D8B", fg="white", width=15).pack(side='left', padx=5)
        
        # Treeview để hiển thị danh sách
        tree_frame = tk.Frame(self.current_frame)
        tree_frame.pack(expand=True, fill='both')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Treeview
        columns = ('service', 'username', 'notes')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', 
                                yscrollcommand=scrollbar.set)
        
        self.tree.heading('service', text='Dịch vụ')
        self.tree.heading('username', text='Username')
        self.tree.heading('notes', text='Ghi chú')
        
        self.tree.column('service', width=200)
        self.tree.column('username', width=200)
        self.tree.column('notes', width=350)
        
        self.tree.pack(expand=True, fill='both')
        scrollbar.config(command=self.tree.yview)
        
        # Bind double click to edit
        self.tree.bind('<Double-1>', lambda e: self.edit_entry())
        
        # Bind clicks to reset timer
        self.tree.bind('<Button-1>', lambda e: self.reset_activity_timer())
        
        # Load data
        self.refresh_tree()
    
    def refresh_tree(self):
        """Làm mới danh sách entries"""
        # Xóa tất cả items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Load entries
        entries = self.vault.get_entries()
        for entry in entries:
            self.tree.insert('', 'end', values=(entry.service, entry.username, entry.notes))
        
        self.reset_activity_timer()
    
    def add_entry(self):
        """Thêm entry mới"""
        self.reset_activity_timer()
        self.show_entry_dialog(None)
    
    def edit_entry(self):
        """Sửa entry đã chọn"""
        self.reset_activity_timer()
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một entry để sửa")
            return
        
        # Lấy index
        index = self.tree.index(selection[0])
        entry = self.vault.entries[index]
        
        self.show_entry_dialog(index, entry)
    
    def delete_entry(self):
        """Xóa entry đã chọn"""
        self.reset_activity_timer()
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một entry để xóa")
            return
        
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa entry này?"):
            index = self.tree.index(selection[0])
            if self.vault.delete_entry(index):
                self.refresh_tree()
                messagebox.showinfo("Thành công", "Đã xóa entry")
            else:
                messagebox.showerror("Lỗi", "Không thể xóa entry")
    
    def copy_password(self):
        """Sao chép password vào clipboard"""
        self.reset_activity_timer()
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một entry để copy password")
            return
        
        index = self.tree.index(selection[0])
        entry = self.vault.entries[index]
        
        copy_to_clipboard_temporary(entry.password, 20)
        messagebox.showinfo("Thành công", "Password đã được copy vào clipboard (sẽ tự xóa sau 20 giây)")
    
    def lock_vault(self):
        """Khóa vault"""
        if messagebox.askyesno("Xác nhận", "Bạn có muốn khóa vault?"):
            self.vault.save()
            self.vault.lock()
            if self.auto_lock_timer:
                self.auto_lock_timer.cancel()
            self.show_login_screen()
    
    def show_entry_dialog(self, index: Optional[int], entry: Optional[VaultEntry] = None):
        """Hiển thị dialog để thêm/sửa entry"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Thêm Entry" if entry is None else "Sửa Entry")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Form
        form_frame = tk.Frame(dialog)
        form_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        tk.Label(form_frame, text="Dịch vụ:", font=("Arial", 11)).grid(row=0, column=0, sticky='w', pady=5)
        service_entry = tk.Entry(form_frame, width=40, font=("Arial", 11))
        service_entry.grid(row=0, column=1, pady=5, columnspan=2)
        
        tk.Label(form_frame, text="Username:", font=("Arial", 11)).grid(row=1, column=0, sticky='w', pady=5)
        username_entry = tk.Entry(form_frame, width=40, font=("Arial", 11))
        username_entry.grid(row=1, column=1, pady=5, columnspan=2)
        
        tk.Label(form_frame, text="Password:", font=("Arial", 11)).grid(row=2, column=0, sticky='w', pady=5)
        password_entry = tk.Entry(form_frame, width=30, font=("Arial", 11))
        password_entry.grid(row=2, column=1, pady=5)
        
        def generate_and_fill():
            password = generate_password(16)
            password_entry.delete(0, tk.END)
            password_entry.insert(0, password)
        
        tk.Button(form_frame, text="Sinh", command=generate_and_fill, 
                 font=("Arial", 9), bg="#9C27B0", fg="white").grid(row=2, column=2, pady=5, padx=5)
        
        tk.Label(form_frame, text="Ghi chú:", font=("Arial", 11)).grid(row=3, column=0, sticky='nw', pady=5)
        notes_text = tk.Text(form_frame, width=40, height=8, font=("Arial", 10))
        notes_text.grid(row=3, column=1, pady=5, columnspan=2)
        
        # Fill data if editing
        if entry:
            service_entry.insert(0, entry.service)
            username_entry.insert(0, entry.username)
            password_entry.insert(0, entry.password)
            notes_text.insert('1.0', entry.notes)
        
        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def on_save():
            service = service_entry.get().strip()
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            notes = notes_text.get('1.0', 'end').strip()
            
            is_valid, error_msg = validate_entry_data(service, username, password)
            if not is_valid:
                messagebox.showerror("Lỗi", error_msg)
                return
            
            new_entry = VaultEntry(service, username, password, notes)
            
            if index is None:
                # Add new
                if self.vault.add_entry(new_entry):
                    messagebox.showinfo("Thành công", "Đã thêm entry mới")
                    dialog.destroy()
                    self.refresh_tree()
                else:
                    messagebox.showerror("Lỗi", "Không thể thêm entry")
            else:
                # Update existing
                if self.vault.update_entry(index, new_entry):
                    messagebox.showinfo("Thành công", "Đã cập nhật entry")
                    dialog.destroy()
                    self.refresh_tree()
                else:
                    messagebox.showerror("Lỗi", "Không thể cập nhật entry")
        
        tk.Button(button_frame, text="Lưu", command=on_save, 
                 font=("Arial", 11), bg="#4CAF50", fg="white", width=15).pack(side='left', padx=5)
        tk.Button(button_frame, text="Hủy", command=dialog.destroy, 
                 font=("Arial", 11), bg="#757575", fg="white", width=15).pack(side='left', padx=5)
    
    def show_password_generator(self):
        """Hiển thị dialog sinh password"""
        self.reset_activity_timer()
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Sinh Password Ngẫu Nhiên")
        dialog.geometry("450x350")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Length
        tk.Label(dialog, text="Độ dài password:", font=("Arial", 11)).pack(pady=10)
        length_var = tk.IntVar(value=16)
        length_spinner = tk.Spinbox(dialog, from_=4, to=64, textvariable=length_var, 
                                   width=10, font=("Arial", 11))
        length_spinner.pack()
        
        # Options
        options_frame = tk.Frame(dialog)
        options_frame.pack(pady=15)
        
        use_uppercase = tk.BooleanVar(value=True)
        use_lowercase = tk.BooleanVar(value=True)
        use_digits = tk.BooleanVar(value=True)
        use_symbols = tk.BooleanVar(value=True)
        
        tk.Checkbutton(options_frame, text="Chữ hoa (A-Z)", variable=use_uppercase, 
                      font=("Arial", 10)).pack(anchor='w')
        tk.Checkbutton(options_frame, text="Chữ thường (a-z)", variable=use_lowercase, 
                      font=("Arial", 10)).pack(anchor='w')
        tk.Checkbutton(options_frame, text="Số (0-9)", variable=use_digits, 
                      font=("Arial", 10)).pack(anchor='w')
        tk.Checkbutton(options_frame, text="Ký tự đặc biệt (!@#$...)", variable=use_symbols, 
                      font=("Arial", 10)).pack(anchor='w')
        
        # Result
        tk.Label(dialog, text="Password được sinh:", font=("Arial", 11)).pack(pady=5)
        result_entry = tk.Entry(dialog, width=40, font=("Arial", 11))
        result_entry.pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=15)
        
        def generate():
            password = generate_password(
                length=length_var.get(),
                use_uppercase=use_uppercase.get(),
                use_lowercase=use_lowercase.get(),
                use_digits=use_digits.get(),
                use_symbols=use_symbols.get()
            )
            result_entry.delete(0, tk.END)
            result_entry.insert(0, password)
        
        def copy():
            password = result_entry.get()
            if password:
                copy_to_clipboard_temporary(password, 20)
                messagebox.showinfo("Thành công", "Password đã được copy (tự xóa sau 20 giây)")
        
        tk.Button(button_frame, text="Sinh Password", command=generate, 
                 font=("Arial", 10), bg="#9C27B0", fg="white", width=15).pack(side='left', padx=5)
        tk.Button(button_frame, text="Copy", command=copy, 
                 font=("Arial", 10), bg="#FF9800", fg="white", width=15).pack(side='left', padx=5)
        tk.Button(button_frame, text="Đóng", command=dialog.destroy, 
                 font=("Arial", 10), bg="#757575", fg="white", width=15).pack(side='left', padx=5)
        
        # Auto generate first time
        generate()

    def show_change_master_dialog(self):
        """Dialog đổi master password (an toàn, re-key vault)."""
        self.reset_activity_timer()
        dialog = tk.Toplevel(self.root)
        dialog.title("Đổi Master Password")
        dialog.geometry("520x300")
        dialog.transient(self.root)
        dialog.grab_set()

        form = tk.Frame(dialog)
        form.pack(expand=True, fill='both', padx=20, pady=20)

        tk.Label(form, text="Mật khẩu hiện tại:", font=("Arial", 11)).grid(row=0, column=0, sticky='w', pady=8)
        current_entry = tk.Entry(form, show="*", width=40, font=("Arial", 11))
        current_entry.grid(row=0, column=1, pady=8)

        tk.Label(form, text="Mật khẩu mới:", font=("Arial", 11)).grid(row=1, column=0, sticky='w', pady=8)
        new_entry = tk.Entry(form, show="*", width=40, font=("Arial", 11))
        new_entry.grid(row=1, column=1, pady=8)

        tk.Label(form, text="Xác nhận mật khẩu mới:", font=("Arial", 11)).grid(row=2, column=0, sticky='w', pady=8)
        confirm_entry = tk.Entry(form, show="*", width=40, font=("Arial", 11))
        confirm_entry.grid(row=2, column=1, pady=8)

        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)

        def do_change():
            current_pw = current_entry.get()
            new_pw = new_entry.get()
            confirm_pw = confirm_entry.get()

            if new_pw != confirm_pw:
                messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp")
                return

            is_valid, error_msg = validate_master_password(new_pw)
            if not is_valid:
                messagebox.showerror("Lỗi", error_msg)
                return

            # Tiến hành đổi master password (re-key)
            ok = self.vault.change_master_password(current_pw, new_pw)
            if ok:
                messagebox.showinfo("Thành công", "Đã đổi master password. Hãy ghi nhớ mật khẩu mới!")
                dialog.destroy()
                self.reset_activity_timer()
            else:
                messagebox.showerror("Lỗi", "Mật khẩu hiện tại không đúng hoặc có lỗi xảy ra")

        tk.Button(button_frame, text="Đổi mật khẩu", command=do_change, 
                 font=("Arial", 11), bg="#607D8B", fg="white", width=16).pack(side='left', padx=6)
        tk.Button(button_frame, text="Hủy", command=dialog.destroy, 
                 font=("Arial", 11), bg="#757575", fg="white", width=12).pack(side='left', padx=6)

