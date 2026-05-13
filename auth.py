# auth.py
import hashlib
import re
from cryptography.fernet import Fernet
import streamlit as st

# --- 1. CONFIGURATION & SECRET KEY ---
# Trong thực tế, Key này phải được lưu trong biến môi trường (.env)
# Ở đây đặt cứng để tiện cho việc chấm đồ án
SECRET_KEY = b'v_M_L8x-W39rG8Q3YwZ7_hQ8z_T4u_K8_L8x-W39rG8='
cipher = Fernet(SECRET_KEY)

# --- 2. HỆ THỐNG MÃ HÓA (CRYPTOGRAPHY) ---
def encrypt_pii(text):
    """Mã hóa Dữ liệu Nhạy cảm (PII) như Số điện thoại"""
    if not text: return None
    return cipher.encrypt(str(text).encode('utf-8')).decode('utf-8')

def decrypt_pii(crypto_text):
    """Giải mã Dữ liệu Nhạy cảm"""
    if not crypto_text: return None
    try:
        return cipher.decrypt(crypto_text.encode('utf-8')).decode('utf-8')
    except Exception:
        return "[Protected Data]"

# --- 3. HỆ THỐNG PHÂN QUYỀN (RBAC) ---
# Mật khẩu chung cho tất cả các tài khoản test là: 123456
USERS_DB = {
    "admin": {"pwd": hashlib.sha256(b"123456").hexdigest(), "role": "Admin"},
    "sales": {"pwd": hashlib.sha256(b"123456").hexdigest(), "role": "Sales"},
    "finance": {"pwd": hashlib.sha256(b"123456").hexdigest(), "role": "Finance"}
}

def authenticate_user(username, password):
    """Xác thực người dùng và trả về Role"""
    if username in USERS_DB:
        user_record = USERS_DB[username]
        hashed_input = hashlib.sha256(password.encode('utf-8')).hexdigest()
        if hashed_input == user_record["pwd"]:
            return True, user_record["role"]
    return False, None

# --- 4. VALIDATION KHẮT KHE (NEU STANDARD) ---
def validate_contract_form(phone, email, value):
    """Kiểm tra tính hợp lệ của dữ liệu đầu vào trước khi lưu DB"""
    errors = []
    
    # Validate Phone (Chỉ chứa số, độ dài 9-11)
    if not phone.isdigit() or not (9 <= len(phone) <= 11):
        errors.append("Invalid Phone Number format.")
        
    # Validate Email
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email):
        errors.append("Invalid Email format.")
        
    # Validate Value (Không được âm)
    if value is not None and value <= 0:
        errors.append("Contract Value must be greater than zero.")
        
    return len(errors) == 0, errors
