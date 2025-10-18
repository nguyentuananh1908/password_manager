"""
utils.py - Các hàm tiện ích cho Password Manager

Bao gồm:
- Sinh mật khẩu ngẫu nhiên an toàn
- Sao chép vào clipboard với tự động xóa
- Validate input
"""

import secrets
import string
import threading
import pyperclip


def generate_password(length: int = 16, use_uppercase: bool = True, 
                     use_lowercase: bool = True, use_digits: bool = True, 
                     use_symbols: bool = True) -> str:
    """
    Sinh mật khẩu ngẫu nhiên an toàn sử dụng secrets module
    
    Args:
        length: Độ dài mật khẩu (mặc định 16)
        use_uppercase: Sử dụng chữ in hoa
        use_lowercase: Sử dụng chữ thường
        use_digits: Sử dụng số
        use_symbols: Sử dụng ký tự đặc biệt
        
    Returns:
        Mật khẩu ngẫu nhiên
    """
    if length < 4:
        length = 4
    
    # Tạo bộ ký tự
    characters = ""
    if use_lowercase:
        characters += string.ascii_lowercase
    if use_uppercase:
        characters += string.ascii_uppercase
    if use_digits:
        characters += string.digits
    if use_symbols:
        characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    if not characters:
        # Nếu không chọn gì, mặc định dùng tất cả
        characters = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # Sinh mật khẩu ngẫu nhiên an toàn
    password = ''.join(secrets.choice(characters) for _ in range(length))
    
    return password


def copy_to_clipboard_temporary(text: str, duration: int = 20):
    """
    Sao chép text vào clipboard và tự động xóa sau một khoảng thời gian
    
    Args:
        text: Nội dung cần copy
        duration: Thời gian tồn tại (giây), mặc định 20 giây
    """
    # Copy vào clipboard
    pyperclip.copy(text)
    
    # Tạo timer để xóa sau duration giây
    def clear_clipboard():
        # Chỉ xóa nếu clipboard vẫn chứa text gốc
        try:
            current = pyperclip.paste()
            if current == text:
                pyperclip.copy("")
        except:
            pass
    
    timer = threading.Timer(duration, clear_clipboard)
    timer.daemon = True
    timer.start()


def validate_master_password(password: str) -> tuple[bool, str]:
    """
    Kiểm tra độ mạnh của master password
    
    Args:
        password: Mật khẩu cần kiểm tra
        
    Returns:
        Tuple (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Master password phải có ít nhất 8 ký tự"
    
    # Khuyến nghị mật khẩu mạnh
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    if not (has_upper and has_lower and has_digit):
        return False, "Master password nên có chữ hoa, chữ thường và số"
    
    return True, ""


def validate_entry_data(service: str, username: str, password: str) -> tuple[bool, str]:
    """
    Kiểm tra dữ liệu entry trước khi lưu
    
    Args:
        service: Tên dịch vụ
        username: Tên người dùng
        password: Mật khẩu
        
    Returns:
        Tuple (is_valid, error_message)
    """
    if not service or not service.strip():
        return False, "Tên dịch vụ không được để trống"
    
    if not username or not username.strip():
        return False, "Username không được để trống"
    
    if not password or not password.strip():
        return False, "Password không được để trống"
    
    return True, ""

