"""
vault.py - Module xử lý mã hóa/giải mã vault với AES-256-GCM và Argon2id

Cơ chế bảo mật:
- Sử dụng Argon2id để derive khóa mã hóa từ master password
- Mã hóa toàn bộ dữ liệu bằng AES-256-GCM (authenticated encryption)
- Salt ngẫu nhiên 16 bytes cho mỗi vault
- Nonce ngẫu nhiên 12 bytes cho mỗi lần mã hóa
- Không lưu khóa hay master password dưới dạng plaintext
"""

import os
import json
import base64
from typing import Optional, Dict, List
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from argon2 import PasswordHasher
from argon2.low_level import hash_secret_raw, Type


class VaultEntry:
    """Đại diện cho một entry trong vault (một tài khoản được lưu)"""
    
    def __init__(self, service: str, username: str, password: str, notes: str = ""):
        self.service = service
        self.username = username
        self.password = password
        self.notes = notes
    
    def to_dict(self) -> dict:
        return {
            'service': self.service,
            'username': self.username,
            'password': self.password,
            'notes': self.notes
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'VaultEntry':
        return VaultEntry(
            service=data.get('service', ''),
            username=data.get('username', ''),
            password=data.get('password', ''),
            notes=data.get('notes', '')
        )


class Vault:
    """
    Vault - Kho lưu trữ mật khẩu được mã hóa
    
    Cấu trúc file vault.enc:
    - Salt (16 bytes) - dùng cho Argon2id KDF
    - Nonce (12 bytes) - IV cho AES-GCM
    - Ciphertext + Auth Tag - dữ liệu đã mã hóa
    """
    
    def __init__(self, vault_path: str = "vault.enc"):
        self.vault_path = vault_path
        self.entries: List[VaultEntry] = []
        self.is_unlocked = False
        self._encryption_key: Optional[bytes] = None
        self._salt: Optional[bytes] = None
    
    def create_new_vault(self, master_password: str) -> bool:
        """
        Tạo vault mới với master password
        
        Args:
            master_password: Mật khẩu chính để mã hóa vault
            
        Returns:
            True nếu tạo thành công
        """
        try:
            # Sinh salt ngẫu nhiên 16 bytes
            self._salt = os.urandom(16)
            
            # Derive khóa mã hóa từ master password sử dụng Argon2id
            self._encryption_key = self._derive_key(master_password, self._salt)
            
            # Khởi tạo vault trống
            self.entries = []
            self.is_unlocked = True
            
            # Lưu vault
            self.save()
            
            return True
        except Exception as e:
            print(f"Error creating vault: {e}")
            return False
    
    def unlock(self, master_password: str) -> bool:
        """
        Mở khóa vault với master password
        
        Args:
            master_password: Mật khẩu chính
            
        Returns:
            True nếu mở khóa thành công, False nếu sai mật khẩu hoặc lỗi
        """
        try:
            if not os.path.exists(self.vault_path):
                return False
            
            # Đọc file vault
            with open(self.vault_path, 'rb') as f:
                vault_data = f.read()
            
            # Tách salt (16 bytes đầu tiên)
            self._salt = vault_data[:16]
            
            # Derive khóa từ master password
            self._encryption_key = self._derive_key(master_password, self._salt)
            
            # Tách nonce (12 bytes tiếp theo)
            nonce = vault_data[16:28]
            
            # Tách ciphertext (phần còn lại)
            ciphertext = vault_data[28:]
            
            # Giải mã dữ liệu
            aesgcm = AESGCM(self._encryption_key)
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            
            # Parse JSON
            data = json.loads(plaintext.decode('utf-8'))
            
            # Load entries
            self.entries = [VaultEntry.from_dict(e) for e in data.get('entries', [])]
            
            self.is_unlocked = True
            return True
            
        except Exception as e:
            # Giải mã thất bại = sai mật khẩu hoặc file bị corrupt
            self.is_unlocked = False
            self._encryption_key = None
            self._salt = None
            return False
    
    def lock(self):
        """Khóa vault và xóa khóa mã hóa khỏi bộ nhớ"""
        self.is_unlocked = False
        self._encryption_key = None
        self.entries = []
    
    def save(self) -> bool:
        """
        Lưu vault vào file (mã hóa toàn bộ)
        
        Returns:
            True nếu lưu thành công
        """
        if not self.is_unlocked or self._encryption_key is None:
            return False
        
        try:
            # Chuẩn bị dữ liệu
            data = {
                'entries': [e.to_dict() for e in self.entries]
            }
            
            # Chuyển sang JSON
            plaintext = json.dumps(data, ensure_ascii=False).encode('utf-8')
            
            # Sinh nonce ngẫu nhiên 12 bytes cho AES-GCM
            nonce = os.urandom(12)
            
            # Mã hóa dữ liệu với AES-256-GCM
            aesgcm = AESGCM(self._encryption_key)
            ciphertext = aesgcm.encrypt(nonce, plaintext, None)
            
            # Ghi file: salt + nonce + ciphertext
            with open(self.vault_path, 'wb') as f:
                f.write(self._salt)
                f.write(nonce)
                f.write(ciphertext)
            
            return True
            
        except Exception as e:
            print(f"Error saving vault: {e}")
            return False
    
    def add_entry(self, entry: VaultEntry) -> bool:
        """Thêm entry mới vào vault"""
        if not self.is_unlocked:
            return False
        
        self.entries.append(entry)
        return self.save()
    
    def update_entry(self, index: int, entry: VaultEntry) -> bool:
        """Cập nhật entry tại vị trí index"""
        if not self.is_unlocked or index < 0 or index >= len(self.entries):
            return False
        
        self.entries[index] = entry
        return self.save()
    
    def delete_entry(self, index: int) -> bool:
        """Xóa entry tại vị trí index"""
        if not self.is_unlocked or index < 0 or index >= len(self.entries):
            return False
        
        del self.entries[index]
        return self.save()
    
    def get_entries(self) -> List[VaultEntry]:
        """Lấy danh sách tất cả entries"""
        if not self.is_unlocked:
            return []
        return self.entries.copy()
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """
        Derive khóa mã hóa 32 bytes từ master password sử dụng Argon2id
        
        Tham số Argon2id:
        - time_cost: số lần lặp
        - memory_cost: bộ nhớ sử dụng (KB)
        - parallelism: số luồng song song
        - hash_len: độ dài khóa đầu ra (32 bytes = 256 bits)
        
        Args:
            password: Master password
            salt: Salt ngẫu nhiên
            
        Returns:
            Khóa mã hóa 32 bytes
        """
        key = hash_secret_raw(
            secret=password.encode('utf-8'),
            salt=salt,
            time_cost=3,        # Số lần lặp
            memory_cost=65536,  # 64 MB
            parallelism=4,      # 4 luồng
            hash_len=32,        # 256 bits
            type=Type.ID        # Argon2id
        )
        return key
    
    def vault_exists(self) -> bool:
        """Kiểm tra xem vault đã tồn tại chưa"""
        return os.path.exists(self.vault_path)

    def change_master_password(self, current_password: str, new_password: str) -> bool:
        """
        Đổi master password và giữ nguyên dữ liệu (re-key vault).

        Quy trình an toàn:
        1) Đọc file hiện tại, lấy salt cũ, nonce, ciphertext
        2) Derive khóa cũ từ current_password + salt cũ, giải mã để lấy plaintext
        3) Tạo salt mới 16 bytes, derive khóa mới từ new_password + salt mới
        4) Ghi lại vault với salt mới và nonce mới (AES-256-GCM)

        Trả về True nếu thành công, False nếu current_password sai hoặc lỗi khác.
        """
        try:
            if not os.path.exists(self.vault_path):
                return False

            # Đọc file vault
            with open(self.vault_path, 'rb') as f:
                vault_data = f.read()

            old_salt = vault_data[:16]
            nonce = vault_data[16:28]
            ciphertext = vault_data[28:]

            # Giải mã bằng mật khẩu hiện tại
            old_key = self._derive_key(current_password, old_salt)
            aesgcm = AESGCM(old_key)
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)

            # Parse entries từ plaintext
            data = json.loads(plaintext.decode('utf-8'))
            new_entries = [VaultEntry.from_dict(e) for e in data.get('entries', [])]

            # Tạo salt mới và derive khóa mới
            new_salt = os.urandom(16)
            new_key = self._derive_key(new_password, new_salt)

            # Cập nhật trạng thái bộ nhớ và lưu lại với khóa mới
            self._salt = new_salt
            self._encryption_key = new_key
            self.entries = new_entries
            self.is_unlocked = True

            return self.save()

        except Exception:
            # Nếu giải mã thất bại hoặc lỗi khác -> trả về False, không lộ chi tiết
            return False

