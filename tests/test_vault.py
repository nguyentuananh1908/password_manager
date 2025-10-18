"""
test_vault.py - Unit tests cho Password Manager

Chạy tests: python test_vault.py
"""

import unittest
import os
from app.vault import Vault, VaultEntry


class TestVault(unittest.TestCase):
    """Test cases cho Vault class"""
    
    def setUp(self):
        """Thiết lập trước mỗi test"""
        self.test_vault_path = "test_vault.enc"
        self.master_password = "TestPassword123!"
        self.vault = Vault(self.test_vault_path)
    
    def tearDown(self):
        """Dọn dẹp sau mỗi test"""
        if os.path.exists(self.test_vault_path):
            os.remove(self.test_vault_path)
    
    def test_create_new_vault(self):
        """Test tạo vault mới"""
        result = self.vault.create_new_vault(self.master_password)
        self.assertTrue(result)
        self.assertTrue(self.vault.is_unlocked)
        self.assertTrue(os.path.exists(self.test_vault_path))
    
    def test_unlock_vault_correct_password(self):
        """Test mở vault với mật khẩu đúng"""
        # Tạo vault
        self.vault.create_new_vault(self.master_password)
        self.vault.lock()
        
        # Mở lại với mật khẩu đúng
        result = self.vault.unlock(self.master_password)
        self.assertTrue(result)
        self.assertTrue(self.vault.is_unlocked)
    
    def test_unlock_vault_wrong_password(self):
        """Test mở vault với mật khẩu sai"""
        # Tạo vault
        self.vault.create_new_vault(self.master_password)
        self.vault.lock()
        
        # Mở với mật khẩu sai
        result = self.vault.unlock("WrongPassword123!")
        self.assertFalse(result)
        self.assertFalse(self.vault.is_unlocked)
    
    def test_add_entry(self):
        """Test thêm entry vào vault"""
        self.vault.create_new_vault(self.master_password)
        
        entry = VaultEntry("Gmail", "user@gmail.com", "password123", "My email")
        result = self.vault.add_entry(entry)
        
        self.assertTrue(result)
        self.assertEqual(len(self.vault.entries), 1)
        self.assertEqual(self.vault.entries[0].service, "Gmail")
    
    def test_update_entry(self):
        """Test cập nhật entry"""
        self.vault.create_new_vault(self.master_password)
        
        # Thêm entry
        entry = VaultEntry("Gmail", "user@gmail.com", "password123", "My email")
        self.vault.add_entry(entry)
        
        # Cập nhật entry
        updated_entry = VaultEntry("Gmail", "newuser@gmail.com", "newpass456", "Updated")
        result = self.vault.update_entry(0, updated_entry)
        
        self.assertTrue(result)
        self.assertEqual(self.vault.entries[0].username, "newuser@gmail.com")
        self.assertEqual(self.vault.entries[0].password, "newpass456")
    
    def test_delete_entry(self):
        """Test xóa entry"""
        self.vault.create_new_vault(self.master_password)
        
        # Thêm entries
        self.vault.add_entry(VaultEntry("Gmail", "user@gmail.com", "pass1", ""))
        self.vault.add_entry(VaultEntry("Facebook", "user@fb.com", "pass2", ""))
        
        self.assertEqual(len(self.vault.entries), 2)
        
        # Xóa entry đầu tiên
        result = self.vault.delete_entry(0)
        
        self.assertTrue(result)
        self.assertEqual(len(self.vault.entries), 1)
        self.assertEqual(self.vault.entries[0].service, "Facebook")
    
    def test_persistence(self):
        """Test lưu trữ và load lại dữ liệu"""
        # Tạo vault và thêm entries
        self.vault.create_new_vault(self.master_password)
        self.vault.add_entry(VaultEntry("Gmail", "user@gmail.com", "pass1", "Note 1"))
        self.vault.add_entry(VaultEntry("Facebook", "user@fb.com", "pass2", "Note 2"))
        self.vault.lock()
        
        # Tạo vault mới và load từ file
        new_vault = Vault(self.test_vault_path)
        result = new_vault.unlock(self.master_password)
        
        self.assertTrue(result)
        self.assertEqual(len(new_vault.entries), 2)
        self.assertEqual(new_vault.entries[0].service, "Gmail")
        self.assertEqual(new_vault.entries[1].service, "Facebook")
        self.assertEqual(new_vault.entries[0].notes, "Note 1")
    
    def test_lock_vault(self):
        """Test khóa vault"""
        self.vault.create_new_vault(self.master_password)
        self.vault.add_entry(VaultEntry("Gmail", "user@gmail.com", "pass1", ""))
        
        self.assertTrue(self.vault.is_unlocked)
        
        # Khóa vault
        self.vault.lock()
        
        self.assertFalse(self.vault.is_unlocked)
        self.assertEqual(len(self.vault.entries), 0)  # Entries đã bị xóa khỏi bộ nhớ
    
    def test_encryption_different_nonce(self):
        """Test mỗi lần lưu sử dụng nonce khác nhau"""
        self.vault.create_new_vault(self.master_password)
        self.vault.add_entry(VaultEntry("Test", "test", "test", ""))
        
        # Đọc file vault lần 1
        with open(self.test_vault_path, 'rb') as f:
            data1 = f.read()
        
        # Lưu lại
        self.vault.save()
        
        # Đọc file vault lần 2
        with open(self.test_vault_path, 'rb') as f:
            data2 = f.read()
        
        # Salt giống nhau (16 bytes đầu)
        self.assertEqual(data1[:16], data2[:16])
        
        # Nonce khác nhau (12 bytes tiếp theo)
        self.assertNotEqual(data1[16:28], data2[16:28])
    
    def test_vault_entry_serialization(self):
        """Test serialization của VaultEntry"""
        entry = VaultEntry("Gmail", "user@gmail.com", "password123", "Test note")
        
        # To dict
        entry_dict = entry.to_dict()
        self.assertEqual(entry_dict['service'], "Gmail")
        self.assertEqual(entry_dict['username'], "user@gmail.com")
        
        # From dict
        restored_entry = VaultEntry.from_dict(entry_dict)
        self.assertEqual(restored_entry.service, entry.service)
        self.assertEqual(restored_entry.username, entry.username)
        self.assertEqual(restored_entry.password, entry.password)
        self.assertEqual(restored_entry.notes, entry.notes)


class TestUtils(unittest.TestCase):
    """Test cases cho utils module"""
    
    def test_generate_password_length(self):
        """Test độ dài password được sinh"""
        from app.utils import generate_password
        
        for length in [8, 12, 16, 20, 32]:
            password = generate_password(length)
            self.assertEqual(len(password), length)
    
    def test_generate_password_characters(self):
        """Test ký tự trong password được sinh"""
        from app.utils import generate_password
        import string
        
        # Chỉ số
        password = generate_password(20, use_uppercase=False, use_lowercase=False, 
                                    use_digits=True, use_symbols=False)
        self.assertTrue(all(c in string.digits for c in password))
        
        # Chỉ chữ thường
        password = generate_password(20, use_uppercase=False, use_lowercase=True, 
                                    use_digits=False, use_symbols=False)
        self.assertTrue(all(c in string.ascii_lowercase for c in password))
    
    def test_validate_master_password(self):
        """Test validation master password"""
        from app.utils import validate_master_password
        
        # Password quá ngắn
        is_valid, msg = validate_master_password("short")
        self.assertFalse(is_valid)
        
        # Password không đủ mạnh
        is_valid, msg = validate_master_password("weakpassword")
        self.assertFalse(is_valid)
        
        # Password hợp lệ
        is_valid, msg = validate_master_password("StrongPass123")
        self.assertTrue(is_valid)
    
    def test_validate_entry_data(self):
        """Test validation dữ liệu entry"""
        from app.utils import validate_entry_data
        
        # Dữ liệu hợp lệ
        is_valid, msg = validate_entry_data("Gmail", "user@gmail.com", "password123")
        self.assertTrue(is_valid)
        
        # Service rỗng
        is_valid, msg = validate_entry_data("", "user@gmail.com", "password123")
        self.assertFalse(is_valid)
        
        # Username rỗng
        is_valid, msg = validate_entry_data("Gmail", "", "password123")
        self.assertFalse(is_valid)
        
        # Password rỗng
        is_valid, msg = validate_entry_data("Gmail", "user@gmail.com", "")
        self.assertFalse(is_valid)


def run_tests():
    """Chạy tất cả tests"""
    # Tạo test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Thêm test cases
    suite.addTests(loader.loadTestsFromTestCase(TestVault))
    suite.addTests(loader.loadTestsFromTestCase(TestUtils))
    
    # Chạy tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Kết quả
    print("\n" + "="*70)
    try:
        print(f"Đã chạy {result.testsRun} tests")
        print(f"✓ Thành công: {result.testsRun - len(result.failures) - len(result.errors)}")
        if result.failures:
            print(f"✗ Thất bại: {len(result.failures)}")
        if result.errors:
            print(f"⚠ Lỗi: {len(result.errors)}")
    except UnicodeEncodeError:
        # Fallback cho Windows console không hỗ trợ Unicode
        print(f"Da chay {result.testsRun} tests")
        print(f"Thanh cong: {result.testsRun - len(result.failures) - len(result.errors)}")
        if result.failures:
            print(f"That bai: {len(result.failures)}")
        if result.errors:
            print(f"Loi: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)

