"""
main.py - Entry point cho Password Manager

Chạy ứng dụng (sau tái cấu trúc thư mục):
  - python -m app.main

Ứng dụng Password Manager an toàn với mã hóa AES-256-GCM và Argon2id
"""

import sys
from app.vault import Vault
from app.ui import PasswordManagerUI


def main():
    """Hàm chính để khởi động ứng dụng"""
    print("=== Password Manager ===")
    print("Dang khoi dong...")
    
    # Khởi tạo vault (lưu trong thư mục data/)
    vault = Vault(vault_path="data/vault.enc")
    
    # Khởi tạo giao diện
    app = PasswordManagerUI(vault)
    
    # Chạy ứng dụng
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nUng dung da duoc dong")
        vault.lock()
        sys.exit(0)
    except Exception as e:
        print(f"Loi: {e}")
        vault.lock()
        sys.exit(1)


if __name__ == "__main__":
    main()

