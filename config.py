# config.py
import streamlit as st

# --- 1. TỪ ĐIỂN ĐA NGÔN NGỮ (SẠCH SẼ - CHUẨN MINIMALIST ENTERPRISE) ---
LANGUAGES = {
    "English": {
        # General & Actions
        "app_title": "CM-System Enterprise",
        "search": "Search by Name, Phone, or ID...",
        "save": "Save Changes", "cancel": "Cancel", "delete": "Delete",
        "confirm": "Are you sure you want to proceed?", "success": "Operation completed successfully.",
        "error": "An error occurred while processing.",
        
        # Navigation
        "menu_dash": "Dashboard", "menu_list": "Contract Listing",
        "menu_detail": "Contract Detail", "menu_form": "Create / Edit",
        "menu_admin": "Admin & Security", "logout": "Logout",
        
        # Dashboard KPIs & Charts
        "total_contracts": "Total Contracts", "expiring_soon": "Expiring < 7 Days",
        "total_value": "Total Revenue", "debt": "Outstanding Debt",
        "chart_status": "Contract Status Distribution", "chart_revenue": "Revenue Trend",
        
        # Listing & Detail
        "filters": "Advanced Filters", "partner": "Client / Partner", "status": "Status",
        "metadata": "Contract Metadata", "audit_log": "Audit Log & Timeline", "pdf_viewer": "PDF Document Viewer",
        
        # Form Tabs
        "tab_general": "1. General Information", "tab_finance": "2. Finance & Terms", "tab_attach": "3. Attachments",
        "upload_prompt": "Drag and drop PDF document here",
        
        # Admin & Alerts
        "demo_btn": "Generate 510 Demo Rows", "backup_btn": "Export Database (.sql)",
        "alert_title": "Action Required", "alert_msg": "contract(s) expiring within 7 days.",
        "signed": "Digitally Signed & Verified by CM-System"
    },
    "Tiếng Việt": {
        # General & Actions
        "app_title": "Hệ thống Quản trị CM-System",
        "search": "Tìm kiếm theo Tên, SĐT, hoặc Mã...",
        "save": "Lưu thay đổi", "cancel": "Hủy", "delete": "Xóa",
        "confirm": "Bạn có chắc chắn muốn thực hiện?", "success": "Thao tác thành công.",
        "error": "Có lỗi xảy ra trong quá trình xử lý.",
        
        # Navigation
        "menu_dash": "Bảng điều khiển", "menu_list": "Danh sách Hợp đồng",
        "menu_detail": "Chi tiết Hợp đồng", "menu_form": "Khởi tạo / Chỉnh sửa",
        "menu_admin": "Quản trị Hệ thống", "logout": "Đăng xuất",
        
        # Dashboard KPIs & Charts
        "total_contracts": "Tổng Hợp đồng", "expiring_soon": "Sắp hết hạn (< 7 ngày)",
        "total_value": "Tổng Doanh thu", "debt": "Công nợ quá hạn",
        "chart_status": "Phân bổ Trạng thái", "chart_revenue": "Xu hướng Doanh thu",
        
        # Listing & Detail
        "filters": "Bộ lọc Nâng cao", "partner": "Đối tác / Khách hàng", "status": "Trạng thái",
        "metadata": "Thông tin Siêu dữ liệu", "audit_log": "Lịch sử Hệ thống", "pdf_viewer": "Trình xem PDF",
        
        # Form Tabs
        "tab_general": "1. Thông tin Chung", "tab_finance": "2. Tài chính & Điều khoản", "tab_attach": "3. Tệp đính kèm",
        "upload_prompt": "Kéo thả tài liệu PDF vào đây",
        
        # Admin & Alerts
        "demo_btn": "Khởi tạo 510 Dòng dữ liệu mẫu", "backup_btn": "Sao lưu Cơ sở dữ liệu (.sql)",
        "alert_title": "Yêu cầu Xử lý", "alert_msg": "hợp đồng sẽ hết hạn trong 7 ngày tới.",
        "signed": "Ký số tự động & Xác thực bởi CM-System"
    }
}

# --- 2. ENTERPRISE LIGHT THEME CSS ---
def get_light_theme_css():
    """
    CSS tối ưu cho Light Mode: Nền trắng/xám nhạt, Font Sans-serif (Inter), 
    Bo góc 8px, Bóng đổ siêu nhạt, Status Badges tương phản cao.
    """
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* Typography & Base Variables */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif !important;
            color: #0F172A !important; /* Xám đen Slate */
            background-color: #F8FAFC !important; /* Xám siêu nhạt */
        }
        
        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid #E2E8F0;
            padding-top: 1.5rem;
        }

        /* Clean UI Cards & Metrics (Bo góc 8px, Bóng đổ mờ) */
        [data-testid="stMetric"], .stDataFrame, div.stForm {
            background-color: #FFFFFF !important;
            border-radius: 8px !important;
            border: 1px solid #E2E8F0 !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
            padding: 20px !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        /* Metric Typography */
        [data-testid="stMetricValue"] {
            font-size: 2rem !important;
            font-weight: 700 !important;
            color: #0EA5E9 !important; /* Sky Blue cho điểm nhấn */
        }
        [data-testid="stMetricLabel"] {
            color: #64748B !important;
            font-weight: 500 !important;
            font-size: 1rem !important;
        }

        /* Status Badges */
        .badge-active { background-color: #DCFCE7; color: #166534; padding: 4px 12px; border-radius: 999px; font-weight: 600; font-size: 0.85rem;}
        .badge-pending { background-color: #FEF9C3; color: #854D0E; padding: 4px 12px; border-radius: 999px; font-weight: 600; font-size: 0.85rem;}
        .badge-expired { background-color: #FEE2E2; color: #991B1B; padding: 4px 12px; border-radius: 999px; font-weight: 600; font-size: 0.85rem;}

        /* Alert Banners (Amber/Yellow for warnings) */
        .alert-warning {
            background-color: #FFFBEB;
            border-left: 4px solid #F59E0B;
            color: #92400E;
            padding: 16px;
            border-radius: 6px;
            margin-bottom: 20px;
            font-weight: 500;
        }

        /* Buttons (Primary Action) */
        .stButton>button {
            border-radius: 6px !important;
            font-weight: 600 !important;
        }
        
        /* Tabs styling */
        button[data-baseweb="tab"] {
            font-weight: 600 !important;
            color: #64748B !important;
        }
        button[aria-selected="true"] {
            color: #1E3A8A !important; /* Xanh Navy khi Active */
            border-bottom-color: #1E3A8A !important;
        }
    </style>
    """
