# Password Manager

Ứng dụng quản lý mật khẩu an toàn với giao diện đồ họa (GUI) được viết bằng Python.

## ✨ Tính năng

- 🔐 **Mã hóa mạnh mẽ**: AES-256-GCM cho toàn bộ dữ liệu
- 🔑 **Argon2id KDF**: Derive khóa an toàn từ master password
- ➕ **Quản lý mật khẩu**: Thêm, sửa, xóa, xem mật khẩu
- 🎲 **Sinh mật khẩu ngẫu nhiên**: Tùy chỉnh độ dài và ký tự
- 📋 **Clipboard tạm thời**: Tự động xóa sau 20 giây
- 🔒 **Tự động khóa**: Khóa vault sau 2 phút không hoạt động
- 💾 **Lưu trữ an toàn**: Tất cả dữ liệu được mã hóa trong file duy nhất

## 🔐 Bảo mật

- **AES-256-GCM**: Authenticated encryption với 256-bit key
- **Argon2id**: Key derivation function chống brute-force
- **Random salt**: 16 bytes ngẫu nhiên cho mỗi vault
- **Random nonce**: 12 bytes ngẫu nhiên cho mỗi lần mã hóa
- **Không lưu khóa**: Master password và khóa mã hóa không được lưu dưới dạng plaintext
- **Memory safety**: Xóa khóa khỏi bộ nhớ khi khóa vault

## 📋 Yêu cầu

- Python 3.10 trở lên
- Windows/Linux/macOS
- Tkinter (thường có sẵn trong Python)

## 🚀 Cài đặt

### 1. Clone hoặc tải mã nguồn

```bash
cd Password\ Manager
```

### 2. Cài đặt các thư viện cần thiết

```bash
pip install -r requirements.txt
```

Hoặc cài thủ công:

```bash
pip install cryptography argon2-cffi pyperclip
```

### 3. Chạy ứng dụng

```bash
python -m app.main
```

## 📖 Hướng dẫn sử dụng

### Lần đầu tiên (Tạo vault mới)

1. Chạy `python -m app.main`
2. Ứng dụng sẽ yêu cầu tạo vault mới
3. Nhập **master password** (ít nhất 8 ký tự, nên có chữ hoa, chữ thường, số)
4. Xác nhận lại master password
5. Vault được tạo và lưu vào file `vault.enc`

⚠️ **LƯU Ý**: Master password cực kỳ quan trọng! Nếu quên, bạn sẽ **mất toàn bộ dữ liệu**.

### Mở vault hiện có

1. Chạy `python -m app.main`
2. Nhập master password
3. Vault sẽ được giải mã và hiển thị danh sách mật khẩu

### Thêm mật khẩu mới

1. Click nút **➕ Thêm**
2. Nhập thông tin:
   - **Dịch vụ**: Tên website/app (ví dụ: Gmail, Facebook)
   - **Username**: Email hoặc tên đăng nhập
   - **Password**: Mật khẩu (có thể dùng nút "Sinh" để tạo ngẫu nhiên)
   - **Ghi chú**: Thông tin thêm (không bắt buộc)
3. Click **Lưu**

### Sửa mật khẩu

1. Click chọn entry trong danh sách
2. Click nút **✏️ Sửa** hoặc double-click vào entry
3. Chỉnh sửa thông tin
4. Click **Lưu**

### Xóa mật khẩu

1. Click chọn entry trong danh sách
2. Click nút **🗑️ Xóa**
3. Xác nhận xóa

### Copy mật khẩu

1. Click chọn entry trong danh sách
2. Click nút **📋 Copy Password**
3. Password sẽ được copy vào clipboard
4. Sau 20 giây, clipboard tự động xóa (bảo mật)

### Sinh mật khẩu ngẫu nhiên

1. Click nút **🔑 Sinh Password**
2. Chọn độ dài (4-64 ký tự)
3. Chọn loại ký tự (chữ hoa, chữ thường, số, ký tự đặc biệt)
4. Click **Sinh Password**
5. Password sẽ hiển thị, có thể copy hoặc sinh lại

### Khóa vault

- Click nút **🔒 Khóa** để khóa vault thủ công
- Vault tự động khóa sau **2 phút** không hoạt động
- Khi đóng ứng dụng, vault sẽ được lưu và khóa tự động

### Đổi master
- Click nút ** Đổi master**
- Nhập mật khẩu hiện tại
- Nhập mật khẩu mới , xác nhận mất khẩu mới
- Click đổi mật khẩu -> Đổi thành công

## 📁 Cấu trúc dự án

```
Password Manager/
├── main.py           # Entry point của ứng dụng
├── vault.py          # Module xử lý mã hóa/giải mã
├── ui.py             # Giao diện Tkinter
├── utils.py          # Các hàm tiện ích
├── test_vault.py     # Unit tests
├── requirements.txt  # Danh sách thư viện
├── README.md         # Tài liệu hướng dẫn
└── vault.enc         # File vault được mã hóa (tự động tạo)
```

## 📧 Hỗ trợ

Nếu có vấn đề, hãy kiểm tra:
1. Python version >= 3.10
2. Tất cả thư viện đã được cài đặt
3. Quyền ghi file trong thư mục hiện tại

---

**🔐 Bảo mật là trách nhiệm của bạn! Hãy sử dụng master password mạnh và giữ nó an toàn! 🔐**

