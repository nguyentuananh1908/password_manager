"""
example_usage.py - Ví dụ sử dụng Password Manager qua code

Đây là ví dụ sử dụng vault mà không cần GUI
Hữu ích cho automation hoặc testing
"""

from app.vault import Vault, VaultEntry


def example_create_and_use_vault():
    """Ví dụ tạo vault mới và sử dụng"""
    
    print("=== Ví dụ tạo Vault mới ===\n")
    
    # 1. Tạo vault mới
    vault = Vault("example_vault.enc")
    master_password = "MySecurePassword123!"
    
    print(f"1. Tạo vault với master password: {master_password}")
    if vault.create_new_vault(master_password):
        print("   ✓ Vault đã được tạo thành công!\n")
    else:
        print("   ✗ Lỗi tạo vault\n")
        return
    
    # 2. Thêm một số entries
    print("2. Thêm các entries vào vault:")
    
    entries_to_add = [
        VaultEntry("Gmail", "user@gmail.com", "gmail_password_123", "Email chính"),
        VaultEntry("Facebook", "user@facebook.com", "fb_pass_456", "Tài khoản FB cá nhân"),
        VaultEntry("GitHub", "myusername", "github_token_789", "Dev account"),
    ]
    
    for entry in entries_to_add:
        if vault.add_entry(entry):
            print(f"   ✓ Đã thêm: {entry.service} - {entry.username}")
        else:
            print(f"   ✗ Lỗi thêm: {entry.service}")
    
    print()
    
    # 3. Hiển thị tất cả entries
    print("3. Danh sách tất cả mật khẩu trong vault:")
    print("-" * 80)
    entries = vault.get_entries()
    for i, entry in enumerate(entries, 1):
        print(f"   {i}. {entry.service}")
        print(f"      Username: {entry.username}")
        print(f"      Password: {'*' * len(entry.password)}")  # Không hiển thị password thật
        print(f"      Notes: {entry.notes}")
        print()
    
    # 4. Cập nhật một entry
    print("4. Cập nhật password cho Gmail:")
    updated_entry = VaultEntry("Gmail", "user@gmail.com", "new_secure_password_999", "Email chính - đã update")
    if vault.update_entry(0, updated_entry):
        print("   ✓ Đã cập nhật!\n")
    else:
        print("   ✗ Lỗi cập nhật\n")
    
    # 5. Xóa một entry
    print("5. Xóa entry Facebook:")
    if vault.delete_entry(1):  # Index 1 = Facebook (sau khi đã sắp xếp)
        print("   ✓ Đã xóa!\n")
    else:
        print("   ✗ Lỗi xóa\n")
    
    # 6. Khóa vault
    print("6. Khóa vault:")
    vault.lock()
    print("   ✓ Vault đã bị khóa\n")
    
    # 7. Mở lại vault
    print("7. Mở lại vault với master password:")
    if vault.unlock(master_password):
        print("   ✓ Vault đã được mở!")
        print(f"   Số lượng entries: {len(vault.get_entries())}\n")
    else:
        print("   ✗ Sai password hoặc lỗi\n")
    
    # 8. Thử mở với password sai
    print("8. Thử mở với password sai:")
    vault.lock()
    if vault.unlock("WrongPassword123!"):
        print("   ✓ Mở được (không nên xảy ra!)\n")
    else:
        print("   ✗ Không mở được (đúng như mong đợi!)\n")
    
    # 9. Mở lại và hiển thị entries cuối cùng
    print("9. Danh sách cuối cùng sau các thao tác:")
    vault.unlock(master_password)
    print("-" * 80)
    for i, entry in enumerate(vault.get_entries(), 1):
        print(f"   {i}. {entry.service} - {entry.username}")
    print()
    
    print("=== Hoàn thành! ===")
    print(f"File vault: example_vault.enc")
    print("Bạn có thể mở file này bằng ứng dụng GUI (python main.py)")


def example_password_generator():
    """Ví dụ sử dụng password generator"""
    from app.utils import generate_password
    
    print("\n=== Ví dụ sinh password ngẫu nhiên ===\n")
    
    # Các loại password khác nhau
    examples = [
        ("Password 16 ký tự (mặc định)", {"length": 16}),
        ("Password chỉ chữ và số", {"length": 12, "use_symbols": False}),
        ("Password chỉ số (PIN)", {"length": 6, "use_uppercase": False, 
                                   "use_lowercase": False, "use_symbols": False}),
        ("Password rất mạnh 32 ký tự", {"length": 32}),
    ]
    
    for description, params in examples:
        password = generate_password(**params)
        print(f"{description}:")
        print(f"  → {password}\n")


def example_clipboard():
    """Ví dụ copy vào clipboard tự động xóa"""
    from app.utils import copy_to_clipboard_temporary
    import time
    
    print("\n=== Ví dụ clipboard tự động xóa ===\n")
    
    test_password = "MySecretPassword123!"
    print(f"Copy password vào clipboard: {test_password}")
    print("Password sẽ tự động xóa sau 5 giây...")
    
    copy_to_clipboard_temporary(test_password, 5)
    
    print("Đang đợi 5 giây...")
    for i in range(5, 0, -1):
        print(f"  {i}...", end=" ", flush=True)
        time.sleep(1)
    
    print("\n✓ Clipboard đã được xóa (nếu chưa paste vào đâu khác)")


if __name__ == "__main__":
    import sys
    import os
    
    # Xóa vault ví dụ cũ nếu tồn tại
    if os.path.exists("example_vault.enc"):
        os.remove("example_vault.enc")
    
    try:
        # Chạy các ví dụ
        example_create_and_use_vault()
        example_password_generator()
        
        # Uncomment để test clipboard (cần có X server trên Linux)
        # example_clipboard()
        
    except KeyboardInterrupt:
        print("\n\nĐã hủy bởi người dùng")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nLỗi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

