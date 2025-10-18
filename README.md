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

## 🔧 Cấu trúc file vault.enc

File `vault.enc` có cấu trúc binary:

```
[Salt 16 bytes][Nonce 12 bytes][Encrypted Data + Auth Tag]
```

- **Salt**: Ngẫu nhiên, dùng cho Argon2id KDF
- **Nonce**: Ngẫu nhiên mỗi lần lưu, dùng cho AES-GCM
- **Encrypted Data**: JSON chứa tất cả entries, được mã hóa bằng AES-256-GCM
- **Auth Tag**: 16 bytes, tự động thêm bởi GCM mode để xác thực

## 🧪 Chạy tests

```bash
python test_vault.py
```

Tests sẽ kiểm tra:
- Tạo vault mới
- Mã hóa/giải mã dữ liệu
- Thêm/sửa/xóa entries
- Sai master password

## ❓ FAQ

### Quên master password?

Rất tiếc, **không có cách nào** khôi phục nếu quên master password. Đây là thiết kế bảo mật - không có backdoor.

**Khuyến nghị**: 
- Lưu master password ở nơi an toàn (ghi ra giấy, két sắt)
- Hoặc sử dụng password hint (nhưng đừng quá rõ ràng)


### File vault.enc có an toàn không?

**CÓ**! File này sử dụng mã hóa AES-256-GCM với khóa được derive từ master password qua Argon2id. 

- Không có master password → không thể giải mã
- AES-256 là chuẩn mã hóa quân sự
- Argon2id chống brute-force attack
- GCM mode đảm bảo tính toàn vẹn (tamper detection)

**Tuy nhiên**: Hãy backup file này thường xuyên để tránh mất dữ liệu!

### Tại sao clipboard tự xóa sau 20 giây?

Để bảo mật! Nếu clipboard lưu mật khẩu vĩnh viễn, người khác có thể paste và đánh cắp mật khẩu của bạn sau khi bạn rời máy.

### Có thể thay đổi thời gian tự động khóa không?

Có! Mở file `ui.py` và sửa dòng:

```python
self.auto_lock_time = 120  # Đổi 120 (giây) thành giá trị khác
```

Ví dụ: `300` = 5 phút, `60` = 1 phút, `0` = tắt tự động khóa (không khuyến khích)

### Có thể sync qua cloud không?

Có thể! File `vault.enc` đã được mã hóa hoàn toàn nên an toàn khi lưu trên cloud:

- Đặt file `vault.enc` trong thư mục Dropbox/Google Drive/OneDrive
- Sửa đường dẫn trong `main.py`:
  ```python
  vault = Vault(vault_path="path/to/cloud/vault.enc")
  ```

**Lưu ý**: Tránh mở đồng thời trên nhiều máy để tránh xung đột file!

## 🔒 Chi tiết kỹ thuật bảo mật

### Argon2id Parameters

- **Time cost**: 3 iterations
- **Memory cost**: 64 MB
- **Parallelism**: 4 threads
- **Output**: 32 bytes (256 bits)
- **Type**: Argon2id (hybrid chống side-channel và GPU attacks)

### AES-GCM Parameters

- **Key size**: 256 bits
- **Nonce size**: 12 bytes (96 bits) - recommended size
- **Auth tag**: 16 bytes (128 bits) - auto appended
- **Mode**: GCM (Galois/Counter Mode) - authenticated encryption

### Random Generation

- Sử dụng `os.urandom()` - cryptographically secure random
- Sử dụng `secrets` module cho sinh mật khẩu

### Memory Safety

- Khóa mã hóa chỉ tồn tại trong RAM khi vault unlocked
- Khi lock vault, khóa được set về `None` (Python garbage collector sẽ xóa)
- Master password không bao giờ được lưu

## 🛠️ Troubleshooting

### Lỗi "No module named 'tkinter'"

**Linux**:
```bash
sudo apt-get install python3-tk
```

**macOS**: Tkinter thường có sẵn. Nếu không, cài Python từ python.org

**Windows**: Tkinter có sẵn trong Python installer

### Lỗi khi cài cryptography trên Windows

Cài Visual C++ Build Tools:
https://visualstudio.microsoft.com/visual-cpp-build-tools/

Hoặc sử dụng pre-built wheels:
```bash
pip install --upgrade pip
pip install cryptography
```

### Lỗi "vault bị corrupt"

Nếu file `vault.enc` bị hỏng:
1. Restore từ backup (nếu có)
2. Hoặc xóa file và tạo vault mới (⚠️ mất dữ liệu cũ)

## 📝 License

Mã nguồn mở - Tự do sử dụng và chỉnh sửa.

## ⚠️ Disclaimer

Ứng dụng này được tạo cho mục đích học tập và sử dụng cá nhân. Tác giả không chịu trách nhiệm về mất mát dữ liệu. Hãy **backup thường xuyên** và **ghi nhớ master password**!

## 📧 Hỗ trợ

Nếu có vấn đề, hãy kiểm tra:
1. Python version >= 3.10
2. Tất cả thư viện đã được cài đặt
3. Quyền ghi file trong thư mục hiện tại

---

**🔐 Bảo mật là trách nhiệm của bạn! Hãy sử dụng master password mạnh và giữ nó an toàn! 🔐**

