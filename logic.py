# logic.py
import pandas as pd
import random
from datetime import datetime, timedelta
from fpdf import FPDF
from database import db, execute_query, call_sp_create_invoice
from auth import encrypt_pii, decrypt_pii
import streamlit as st

# --- 1. DASHBOARD & ALERTS ---
def get_kpi_metrics():
    """Truy vấn các chỉ số tổng quan cho Dashboard"""
    rev = execute_query("SELECT SUM(TotalValue) as total_rev FROM Contracts;", fetch_mode="one")
    act = execute_query("SELECT COUNT(*) as active_cnt FROM Contracts WHERE Status = 'Active';", fetch_mode="one")
    debt = execute_query("SELECT SUM(TotalAmount) as total_debt FROM Invoices WHERE Status = 'Unpaid';", fetch_mode="one")
    
    return {
        "revenue": rev['total_rev'] if rev and rev['total_rev'] else 0,
        "active_contracts": act['active_cnt'] if act and act['active_cnt'] else 0,
        "debt": debt['total_debt'] if debt and debt['total_debt'] else 0
    }

def get_expiring_alerts():
    """Lấy danh sách Hợp đồng sắp hết hạn (< 7 ngày)"""
    query = """
        SELECT c.ContractID, cu.CustomerName, 
               DATEDIFF(DATE_ADD(c.SignDate, INTERVAL c.Duration MONTH), CURRENT_DATE) as DaysLeft
        FROM Contracts c
        JOIN Customers cu ON c.CustomerID = cu.CustomerID
        WHERE c.Status = 'Active' 
          AND DATEDIFF(DATE_ADD(c.SignDate, INTERVAL c.Duration MONTH), CURRENT_DATE) BETWEEN 0 AND 7
        ORDER BY DaysLeft ASC;
    """
    return execute_query(query, fetch_mode="all")

# --- 2. AUDIT LOGS ---
def log_action(user, action, details):
    """Ghi lại lịch sử thao tác của người dùng"""
    query = "INSERT INTO AuditLogs (User, Action, Details, Timestamp) VALUES (%s, %s, %s, NOW())"
    execute_query(query, params=(user, action, details), fetch_mode="none")

def get_audit_logs(limit=50):
    query = "SELECT * FROM AuditLogs ORDER BY Timestamp DESC LIMIT %s"
    return execute_query(query, params=(limit,), fetch_mode="all")

# --- 3. CRUD THÔNG MINH ---
def get_contracts_dataframe(role):
    """Lấy danh sách HĐ (JOIN bảng Customers & Services)"""
    query = """
        SELECT c.ContractID, cu.CustomerName, cu.PhoneNumber, s.ServiceName, 
               c.SignDate, c.TotalValue, c.Status
        FROM Contracts c
        JOIN Customers cu ON c.CustomerID = cu.CustomerID
        JOIN Services s ON c.ServiceID = s.ServiceID
        ORDER BY c.SignDate DESC LIMIT 1000;
    """
    data = execute_query(query, fetch_mode="all")
    if not data: return pd.DataFrame()
    
    df = pd.DataFrame(data)
    # Giải mã số điện thoại nếu có quyền
    if role in ["Admin", "Sales"]:
        df['PhoneNumber'] = df['PhoneNumber'].apply(decrypt_pii)
    else:
        df['PhoneNumber'] = "[Restricted]"
    return df

def delete_contract(contract_id, user):
    """Xóa hợp đồng và ghi log"""
    query = "DELETE FROM Contracts WHERE ContractID = %s"
    success = execute_query(query, params=(contract_id,), fetch_mode="none")
    if success:
        log_action(user, "DELETE", f"Deleted contract {contract_id}")
    return success

# --- 4. EXPORT PDF INVOICE ---
def generate_professional_pdf(contract_id, customer_name, amount):
    """Tạo File PDF Hóa đơn bằng fpdf chuẩn Minimalist"""
    pdf = FPDF()
    pdf.add_page()
    
    # Fonts (Dùng Arial nội tại của fpdf để tránh lỗi font)
    pdf.set_font("Arial", 'B', 22)
    pdf.set_text_color(30, 58, 138) # Navy Blue
    
    # Tiêu đề
    pdf.cell(0, 15, "COMMERCIAL INVOICE", ln=True, align='C')
    pdf.ln(10)
    
    # Thông tin Metadata
    pdf.set_font("Arial", '', 12)
    pdf.set_text_color(15, 23, 42) # Slate
    pdf.cell(0, 8, f"Invoice Reference: INV-{contract_id}", ln=True)
    pdf.cell(0, 8, f"Date of Issue: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    pdf.cell(0, 8, f"Billed To: {customer_name}", ln=True)
    
    # Đường kẻ ngang phân cách
    pdf.line(10, 60, 200, 60)
    pdf.ln(15)
    
    # Phần tài chính
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"TOTAL AMOUNT DUE: {amount:,.0f} VND", ln=True)
    
    # Chữ ký số
    pdf.ln(30)
    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 10, "Digitally Signed & Verified by CM-System", ln=True, align='R')
    pdf.cell(0, 5, f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='R')
    
    return pdf.output(dest="S").encode("latin-1")

# --- 5. THE MASTER FEATURE: 510 DEMO ROWS (< 1 SECONDS) ---
def generate_510_demo_rows(user):
    """
    Sử dụng executemany để Batch Insert siêu tốc độ.
    Dữ liệu tên và sđt thuần Việt, chuẩn xác logic.
    """
    conn = db.get_connection()
    if not conn: return False
    
    try:
        cursor = conn.cursor()
        # Tạm tắt kiểm tra khóa ngoại để tăng tốc tối đa
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        
        # 1. Chuẩn bị Dữ liệu mẫu (Thuần Việt)
        last_names = ["Nguyen", "Tran", "Le", "Pham", "Hoang", "Vu", "Vo", "Dang"]
        first_names = ["Anh", "Binh", "Cuong", "Dung", "Hoa", "Lan", "Trang", "Tuan"]
        services = [
            ("S01", "Cloud Infrastructure", "Tech", 15000000),
            ("S02", "Security Audit", "Consulting", 25000000),
            ("S03", "Data Warehouse", "Tech", 40000000)
        ]
        
        # Insert Services (Bỏ qua nếu đã tồn tại)
        cursor.executemany("INSERT IGNORE INTO Services VALUES (%s, %s, %s, %s)", services)
        
        # 2. Sinh dữ liệu khách hàng & Hợp đồng dạng danh sách (List of Tuples)
        customers_data = []
        contracts_data = []
        
        start_date = datetime(2025, 1, 1)
        
        for i in range(1, 511):
            # Khách hàng
            cust_id = f"CUST{i:04d}"
            name = f"{random.choice(last_names)} {random.choice(first_names)} Corp"
            phone = f"09{random.randint(10000000, 99999999)}"
            phone_enc = encrypt_pii(phone)
            email = f"contact{i}@company.vn"
            customers_data.append((cust_id, name, "Hanoi, VN", phone_enc, email))
            
            # Hợp đồng
            cont_id = f"CT{i:04d}"
            srv_id, _, _, base_price = random.choice(services)
            sign_date = start_date + timedelta(days=random.randint(0, 365))
            status = random.choice(["Active", "Active", "Active", "Expired"]) # 75% Active
            
            contracts_data.append((cont_id, cust_id, srv_id, sign_date.strftime('%Y-%m-%d'), 12, base_price, status, 1))

        # 3. Thực thi Batch Insert (Nhanh gấp 100 lần vòng lặp bình thường)
        cursor.executemany("INSERT IGNORE INTO Customers (CustomerID, CustomerName, Address, PhoneNumber, Email) VALUES (%s, %s, %s, %s, %s)", customers_data)
        
        cursor.executemany("INSERT IGNORE INTO Contracts (ContractID, CustomerID, ServiceID, SignDate, Duration, TotalValue, Status, Quantity) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", contracts_data)

        # 4. Commit và Bật lại khóa ngoại
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
        
        log_action(user, "SYSTEM", "Generated 510 Demo Rows successfully.")
        return True

    except Exception as e:
        conn.rollback()
        st.toast(f"Data Generation Failed: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
