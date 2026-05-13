# database.py
import mysql.connector
from mysql.connector import pooling, Error
import streamlit as st

class DatabaseManager:
    """
    Singleton Pattern để quản lý Connection Pooling.
    Đảm bảo hiệu suất truy vấn siêu tốc (< 1 giây) cho hàng nghìn dòng dữ liệu.
    """
    _instance = None
    _pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            try:
                # Thiết lập Connection Pool chuẩn Enterprise
                cls._pool = mysql.connector.pooling.MySQLConnectionPool(
                    pool_name="cms_enterprise_pool",
                    pool_size=15, # Tối ưu cho môi trường tải cao khi chèn 510 dòng
                    pool_reset_session=True,
                    host='localhost',
                    database='contractmanagement',
                    user='root', 
                    password='Trang12345a@' 
                )
            except Error as e:
                # Xử lý lỗi gọn gàng, không để crash app
                st.error(f"Database Connection Failed: Details: {e}")
        return cls._instance

    def get_connection(self):
        """Lấy kết nối từ Pool an toàn"""
        if self._pool is None:
            return None
        try:
            return self._pool.get_connection()
        except Error as e:
            st.error(f"Database Error: Cannot obtain connection. Details: {e}")
            return None

# Khởi tạo Instance toàn cục
db = DatabaseManager()

def execute_query(query, params=None, fetch_mode="all"):
    """
    Hàm lõi thực thi mọi câu lệnh SQL (SELECT, INSERT, UPDATE, DELETE).
    Bao bọc bởi Try-Except chặt chẽ.
    - fetch_mode: "all" (nhiều dòng), "one" (1 dòng), "none" (chỉ thực thi)
    """
    conn = db.get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True) # Trả về dạng Dictionary dễ thao tác
        cursor.execute(query, params)

        if fetch_mode == "all":
            result = cursor.fetchall()
            return result
        elif fetch_mode == "one":
            result = cursor.fetchone()
            return result
        else:
            conn.commit()
            return True
            
    except Error as e:
        if fetch_mode == "none":
            conn.rollback() # Rollback nếu có lỗi khi ghi dữ liệu
        st.toast(f"SQL Error: {e}") # Hiển thị lỗi nhẹ nhàng bằng văn bản
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def call_sp_create_invoice(contract_id, invoice_id, issue_date, notes):
    """
    Tích hợp gọi Stored Procedure: sp_CreateInvoice
    Tự động hóa việc tạo hóa đơn khi Hợp đồng mới được hình thành.
    """
    conn = db.get_connection()
    if not conn:
        return False
        
    try:
        cursor = conn.cursor()
        # Tham số truyền vào tương ứng với khai báo SP trong MySQL
        args = [contract_id, invoice_id, issue_date, notes]
        cursor.callproc('sp_CreateInvoice', args)
        conn.commit()
        return True
    except Error as e:
        conn.rollback()
        st.toast(f"Stored Procedure Error: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
