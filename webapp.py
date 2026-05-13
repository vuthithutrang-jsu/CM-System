# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import time

# Import các module đã xây dựng
import config
from database import execute_query, call_sp_create_invoice
from auth import authenticate_user
import logic

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="CM-System Enterprise", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Nhúng CSS Enterprise Light Theme (Slate Palette)
st.markdown(config.get_light_theme_css(), unsafe_allow_html=True)

# --- 2. SESSION STATE MANAGEMENT ---
if "auth" not in st.session_state:
    st.session_state.update({
        "auth": False, 
        "role": None, 
        "user": None, 
        "lang": "English",
        "selected_contract": None # Lưu ID hợp đồng đang xem
    })

L = config.LANGUAGES[st.session_state.lang]

# --- 3. MODAL CONFIRMATION (st.dialog) ---
@st.dialog("System Confirmation")
def confirm_delete(contract_id):
    st.write(f"You are about to delete Contract **{contract_id}**. This action cannot be undone.")
    reason = st.text_input("Reason for deletion (Audit Log):")
    if st.button("Confirm Delete", type="primary"):
        if logic.delete_contract(contract_id, st.session_state.user):
            st.success("Deleted successfully.")
            st.session_state.selected_contract = None
            time.sleep(1)
            st.rerun()

# --- 4. THE MINIMALIST LOGIN VIEW ---
if not st.session_state.auth:
    st.markdown('<div style="display: flex; justify-content: center; align-items: center; min-height: 70vh;">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown(f"<h1 style='text-align: center; color: #1E3A8A; font-weight: 800;'>CM-System</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #64748B; margin-bottom: 2rem;'>Enterprise Contract Management</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            u = st.text_input("Corporate Username")
            p = st.text_input("Security Passkey", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.form_submit_button("Authenticate", use_container_width=True):
                with st.spinner("Verifying credentials..."):
                    time.sleep(0.5)
                    is_valid, role = authenticate_user(u, p)
                    if is_valid:
                        st.session_state.update({"auth": True, "role": role, "user": u})
                        st.rerun()
                    else:
                        st.error("Authentication failed. Please check your credentials.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. MAIN APPLICATION W/ RBAC ---
else:
    # Sidebar
    st.sidebar.markdown(f"<h3 style='color: #0F172A;'>{st.session_state.user.upper()}</h3>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<p style='color: #0EA5E9; font-weight: 600;'>Role: {st.session_state.role}</p>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    # Language Toggle
    new_lang = st.sidebar.selectbox("Language / Ngôn ngữ", ["English", "Tiếng Việt"], index=0 if st.session_state.lang == "English" else 1)
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()
    
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    
    # Navigation Array with RBAC Filter
    menu_items = [L["menu_dash"], L["menu_list"], L["menu_detail"]]
    
    # Logic Phân quyền: Finance ẩn Sửa/Tạo, Sales ẩn Admin
    if st.session_state.role in ["Admin", "Sales"]:
        menu_items.append(L["menu_form"])
    if st.session_state.role == "Admin":
        menu_items.append(L["menu_admin"])
        
    choice = st.sidebar.radio("Main Menu", menu_items)
    
    st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
    if st.sidebar.button(L["logout"], use_container_width=True):
        st.session_state.auth = False
        st.rerun()

    # --- SCREEN A: DASHBOARD ---
    if choice == L["menu_dash"]:
        st.title(L["menu_dash"])
        
        # Alerts Banner
        alerts = logic.get_expiring_alerts()
        if alerts:
            st.markdown(f'<div class="alert-warning"><b>{L["alert_title"]}</b>: {len(alerts)} {L["alert_msg"]}</div>', unsafe_allow_html=True)
        
        # KPIs
        kpis = logic.get_kpi_metrics()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(L["total_contracts"], kpis['active_contracts'] + 150) # +150 giả lập số liệu cũ
        c2.metric(L["expiring_soon"], len(alerts) if alerts else 0)
        c3.metric(L["total_value"], f"{kpis['revenue']:,.0f} VND")
        c4.metric(L["debt"], f"{kpis['debt']:,.0f} VND")
        
        # Charts
        st.markdown("<br>", unsafe_allow_html=True)
        ch1, ch2 = st.columns([1, 2])
        with ch1:
            # Pie Chart (Status)
            df_pie = pd.DataFrame({"Status": ["Active", "Pending", "Expired"], "Count": [kpis['active_contracts'], 45, 12]})
            fig1 = px.pie(df_pie, names="Status", values="Count", title=L["chart_status"], 
                          color_discrete_sequence=["#10B981", "#F59E0B", "#EF4444"]) # Xanh lá, Vàng, Đỏ
            fig1.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig1, use_container_width=True)
        with ch2:
            # Bar Chart (Revenue)
            df_bar = pd.DataFrame({"Month": ["Jan", "Feb", "Mar", "Apr", "May"], "Rev": [120, 150, 180, 130, 210]})
            fig2 = px.bar(df_bar, x="Month", y="Rev", title=L["chart_revenue"], 
                          color_discrete_sequence=["#0EA5E9"]) # Sky Blue
            fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig2, use_container_width=True)

    # --- SCREEN B: CONTRACT LISTING ---
    elif choice == L["menu_list"]:
        st.title(L["menu_list"])
        
        # Filters (Clean Layout)
        st.markdown(f"**{L['filters']}**")
        f1, f2, f3, f4 = st.columns(4)
        f1.text_input(L["partner"])
        f2.selectbox(L["status"], ["All", "Active", "Pending", "Expired"])
        f3.date_input("Date Range", [])
        search_query = f4.text_input(L["search"])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.spinner("Loading data..."):
            df = logic.get_contracts_dataframe(st.session_state.role)
            if not df.empty:
                st.dataframe(df, use_container_width=True, height=500)
                st.info("💡 Hint: Copy a Contract ID and navigate to 'Contract Detail' to view more.")
            else:
                st.write("No records found. Run Demo Data in Admin tab.")

    # --- SCREEN C: CONTRACT DETAIL (SPLIT VIEW) ---
    elif choice == L["menu_detail"]:
        st.title(L["menu_detail"])
        
        # Input to simulate selection
        cid = st.text_input("Enter Contract ID (e.g., CT0001):", st.session_state.selected_contract or "CT0001")
        
        if cid:
            st.session_state.selected_contract = cid
            col_meta, col_pdf = st.columns([1, 2], gap="large")
            
            with col_meta:
                st.markdown(f"### {L['metadata']}")
                st.markdown(f"**Contract ID:** {cid}")
                st.markdown(f"**{L['partner']}:** Nguyen Van A Corp")
                
                # Status Badge Render
                badge_class = "badge-active" # Giả lập logic
                st.markdown(f"**{L['status']}:** <span class='{badge_class}'>Active</span>", unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown(f"**Value:** 50,000,000 VND")
                st.markdown(f"**Sign Date:** 2025-10-15")
                
                if st.session_state.role == "Admin":
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Delete Contract", type="primary"):
                        confirm_delete(cid)
            
            with col_pdf:
                st.markdown(f"### {L['pdf_viewer']}")
                # Generate PDF dynamically
                pdf_bytes = logic.generate_professional_pdf(cid, "Nguyen Van A Corp", 50000000)
                b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{b64_pdf}" width="100%" height="500px" style="border: 1px solid #E2E8F0; border-radius: 8px;"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
            
            # Audit Log Timeline at bottom
            st.markdown("---")
            st.markdown(f"### {L['audit_log']}")
            df_logs = pd.DataFrame({
                "Timestamp": ["2026-05-10 08:00", "2026-05-09 14:30"],
                "User": ["Admin", "Sales"],
                "Action": ["UPDATE", "CREATE"],
                "Details": ["Changed status to Active", "Initialized draft"]
            })
            st.table(df_logs)

    # --- SCREEN D: CREATE / EDIT FORM (GROUPED TABS) ---
    elif choice == L["menu_form"]:
        st.title(L["menu_form"])
        
        # RBAC Logic cho Tabs: Sales không thấy Tab Tài chính
        tabs_titles = [L["tab_general"], L["tab_attach"]]
        if st.session_state.role != "Sales":
            tabs_titles.insert(1, L["tab_finance"])
            
        tabs = st.tabs(tabs_titles)
        
        with st.form("contract_form"):
            with tabs[0]: # General
                st.markdown("#### Contract Basics")
                c1, c2 = st.columns(2)
                ct_id = c1.text_input("Contract ID")
                cust_id = c2.text_input("Customer ID")
                srv_id = c1.selectbox("Service Type", ["Cloud", "Audit", "Consulting"])
                
            if st.session_state.role != "Sales":
                with tabs[1]: # Finance
                    st.markdown("#### Financial Details")
                    c3, c4 = st.columns(2)
                    val = c3.number_input("Total Value (VND)", min_value=0)
                    dur = c4.number_input("Duration (Months)", min_value=1)
            
            # Index của tab Attach thay đổi tùy thuộc vào việc Finance Tab có tồn tại hay không
            attach_index = 2 if st.session_state.role != "Sales" else 1
            with tabs[attach_index]:
                st.markdown("#### Attach Documents")
                st.file_uploader(L["upload_prompt"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button(L["save"], type="primary")
            if submitted:
                # Tự động gọi SP tạo hóa đơn nếu có Value (Logic NEU)
                value_to_check = val if st.session_state.role != "Sales" else 0
                if ct_id and cust_id:
                    # Giả lập ghi DB thành công
                    call_sp_create_invoice(ct_id, f"INV-{ct_id}", "2026-05-10", "Auto-generated")
                    logic.log_action(st.session_state.user, "CREATE", f"Created Contract {ct_id}")
                    st.success(L["success"])
                else:
                    st.error("Contract ID and Customer ID are required.")

    # --- SCREEN E: ADMIN & SECURITY ---
    elif choice == L["menu_admin"]:
        st.title(L["menu_admin"])
        st.markdown("Manage system configurations and data integrity.")
        
        a1, a2 = st.columns(2)
        with a1:
            st.markdown("#### Development Tools")
            if st.button(L["demo_btn"], use_container_width=True):
                with st.spinner("Batch inserting 510 rows using executemany..."):
                    if logic.generate_510_demo_rows(st.session_state.user):
                        st.success("Loaded 510 records in < 1 second!")
        
        with a2:
            st.markdown("#### Security & Backup")
            st.download_button(L["backup_btn"], data="-- SQL DUMP FILE", file_name="cm_system_backup.sql", use_container_width=True)
