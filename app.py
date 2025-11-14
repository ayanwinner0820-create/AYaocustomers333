# app.py — 完整版（五语、多页面、菜单B、表单完善、导出、备份、权限）
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
from io import BytesIO

from config import PAGE_TITLE, PAGE_ICON, THEME_COLOR, LANG_OPTIONS
from db import init_db
import auth
import customers
import translate
import backup
import logs

# ------------- 初始化 -------------
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide", initial_sidebar_state="expanded")
init_db()

# ------------- 完整翻译字典（翻译方案 1：五种语言） -------------
TRANSLATIONS = {
    "中文": {
        "language_label": "选择语言",
        "menu_navigation": "导航",
        "menu_dashboard": "📊 Dashboard",
        "menu_customers": "👥 客户管理",
        "menu_customers_all": "全部客户",
        "menu_customers_add": "新增客户",
        "menu_followups": "📝 跟进记录",
        "menu_followups_today": "今日跟进",
        "menu_followups_all": "全部跟进",
        "menu_backup": "💾 GitHub 备份",
        "menu_settings": "⚙ 管理设置",
        "menu_users": "用户管理",
        "menu_translations": "翻译管理",
        "menu_logs": "操作日志",
        "login_title": "登录系统",
        "username": "用户名",
        "password": "密码",
        "btn_login": "登录",
        "btn_logout": "退出登录",
        "no_data": "暂无数据",
        "add_customer": "添加客户",
        "submit": "提交",
        "all_customers": "所有客户",
        "search_owner": "按主要负责人搜索",
        "input_customer_id": "输入客户 ID",
        "edit_customer": "编辑客户",
        "delete_customer": "删除客户",
        "confirm_delete": "确认删除该客户",
        "followup_note": "跟进内容",
        "next_action": "下一步动作",
        "followup_added": "跟进记录已创建",
        "level_pie": "客户等级占比",
        "trend": "成交趋势",
        "no_deal": "暂无成交数据",
        "chart_error": "无法生成图表（数据问题）",
        "backup_info": "自动备份使用 Streamlit Secrets: GITHUB_TOKEN / GITHUB_REPO / GITHUB_USERNAME",
        "backup_success": "备份成功",
        "backup_failed": "备份失败：",
        "export_excel": "导出 Excel",
        "owner_export": "导出负责人负责的客户（Excel）",
        "customer_details": "客户详情",
        "created_at": "创建时间",
        "action_logs": "操作日志",
        "add_user": "添加用户",
        "reset_password": "重置密码",
        "delete_user": "删除用户",
        "user_added": "用户已创建",
        "password_reset": "密码已重置",
        "user_deleted": "用户已删除",
        "translations_saved": "翻译已保存",
        "edit_customer_label": "编辑客户信息",
        "no_permission": "权限不足",
    },
    "English": {
        "language_label": "Select language",
        "menu_navigation": "Navigation",
        "menu_dashboard": "📊 Dashboard",
        "menu_customers": "👥 Customers",
        "menu_customers_all": "All Customers",
        "menu_customers_add": "Add Customer",
        "menu_followups": "📝 Followups",
        "menu_followups_today": "Today",
        "menu_followups_all": "All Followups",
        "menu_backup": "💾 GitHub Backup",
        "menu_settings": "⚙ Admin Settings",
        "menu_users": "User Management",
        "menu_translations": "Translations",
        "menu_logs": "Action Logs",
        "login_title": "Login",
        "username": "Username",
        "password": "Password",
        "btn_login": "Login",
        "btn_logout": "Logout",
        "no_data": "No data",
        "add_customer": "Add Customer",
        "submit": "Submit",
        "all_customers": "All Customers",
        "search_owner": "Search by main owner",
        "input_customer_id": "Input customer ID",
        "edit_customer": "Edit customer",
        "delete_customer": "Delete customer",
        "confirm_delete": "Confirm delete this customer",
        "followup_note": "Followup note",
        "next_action": "Next action",
        "followup_added": "Followup added",
        "level_pie": "Level distribution",
        "trend": "Deal trend",
        "no_deal": "No deals",
        "chart_error": "Cannot generate chart (data issue)",
        "backup_info": "Backups use Streamlit Secrets: GITHUB_TOKEN / GITHUB_REPO / GITHUB_USERNAME",
        "backup_success": "Backup success",
        "backup_failed": "Backup failed: ",
        "export_excel": "Export Excel",
        "owner_export": "Export owner's customers (Excel)",
        "customer_details": "Customer details",
        "created_at": "Created at",
        "action_logs": "Action Logs",
        "add_user": "Add user",
        "reset_password": "Reset password",
        "delete_user": "Delete user",
        "user_added": "User added",
        "password_reset": "Password reset",
        "user_deleted": "User deleted",
        "translations_saved": "Translations saved",
        "edit_customer_label": "Edit customer info",
        "no_permission": "No permission",
    },
    "Indonesian": {
        "language_label": "Pilih Bahasa",
        "menu_navigation": "Navigasi",
        "menu_dashboard": "📊 Dashboard",
        "menu_customers": "👥 Pelanggan",
        "menu_customers_all": "Semua Pelanggan",
        "menu_customers_add": "Tambah Pelanggan",
        "menu_followups": "📝 Tindak Lanjut",
        "menu_followups_today": "Hari Ini",
        "menu_followups_all": "Semua Tindak Lanjut",
        "menu_backup": "💾 Cadangan GitHub",
        "menu_settings": "⚙ Pengaturan",
        "menu_users": "Manajemen Pengguna",
        "menu_translations": "Terjemahan",
        "menu_logs": "Log Operasi",
        "login_title": "Masuk",
        "username": "Nama Pengguna",
        "password": "Kata Sandi",
        "btn_login": "Masuk",
        "btn_logout": "Keluar",
        "no_data": "Tidak ada data",
        "add_customer": "Tambah Pelanggan",
        "submit": "Kirim",
        "all_customers": "Semua Pelanggan",
        "search_owner": "Cari berdasarkan penanggung jawab",
        "input_customer_id": "Masukkan ID pelanggan",
        "edit_customer": "Edit pelanggan",
        "delete_customer": "Hapus pelanggan",
        "confirm_delete": "Konfirmasi hapus pelanggan ini",
        "followup_note": "Catatan tindak lanjut",
        "next_action": "Tindakan selanjutnya",
        "followup_added": "Tindak lanjut ditambahkan",
        "level_pie": "Distribusi level",
        "trend": "Tren transaksi",
        "no_deal": "Belum ada transaksi",
        "chart_error": "Tidak dapat membuat grafik (masalah data)",
        "backup_info": "Cadangan menggunakan Streamlit Secrets: GITHUB_TOKEN / GITHUB_REPO / GITHUB_USERNAME",
        "backup_success": "Cadangan berhasil",
        "backup_failed": "Cadangan gagal: ",
        "export_excel": "Ekspor Excel",
        "owner_export": "Ekspor pelanggan penanggung jawab (Excel)",
        "customer_details": "Detail pelanggan",
        "created_at": "Dibuat pada",
        "action_logs": "Log tindakan",
        "add_user": "Tambah pengguna",
        "reset_password": "Atur ulang kata sandi",
        "delete_user": "Hapus pengguna",
        "user_added": "Pengguna ditambahkan",
        "password_reset": "Kata sandi direset",
        "user_deleted": "Pengguna dihapus",
        "translations_saved": "Terjemahan tersimpan",
        "edit_customer_label": "Edit info pelanggan",
        "no_permission": "Tidak punya izin",
    },
    "Khmer": {
        "language_label": "ជ្រើសរើសភាសា",
        "menu_navigation": "ការរុករក",
        "menu_dashboard": "📊 Dashboard",
        "menu_customers": "👥 អតិថិជន",
        "menu_customers_all": "អតិថិជនទាំងអស់",
        "menu_customers_add": "បន្ថែមអតិថិជន",
        "menu_followups": "📝 ដំណើរការ",
        "menu_followups_today": "ថ្ងៃនេះ",
        "menu_followups_all": "ទាំងអស់",
        "menu_backup": "💾 Backup",
        "menu_settings": "⚙ ការកំណត់",
        "menu_users": "គ្រប់គ្រងអ្នកប្រើ",
        "menu_translations": "ការបកប្រែ",
        "menu_logs": "កំណត់ហេតុ",
        "login_title": "ចូលប្រព័ន្ធ",
        "username": "ឈ្មោះអ្នកប្រើ",
        "password": "ពាក្យសម្ងាត់",
        "btn_login": "ចូល",
        "btn_logout": "ចាកចេញ",
        "no_data": "គ្មានទិន្នន័យ",
        "add_customer": "បន្ថែមអតិថិជន",
        "submit": "បញ្ជូន",
        "all_customers": "អតិថិជនទាំងអស់",
        "search_owner": "ស្វែងរកតាមអ្នកទទួលខុសត្រូវ",
        "input_customer_id": "បញ្ចូលលេខសម្គាល់អតិថិជន",
        "edit_customer": "កែសម្រួលអតិថិជន",
        "delete_customer": "លុបអតិថិជន",
        "confirm_delete": "បញ្ជាក់លុបអតិថិជននេះ",
        "followup_note": "កំណត់សម្គាល់",
        "next_action": "សកម្មភាពបន្ទាប់",
        "followup_added": "បានបន្ថែមកំណត់ហេតុ",
        "level_pie": "ចែកចាយកម្រិត",
        "trend": "និន្នាការ",
        "no_deal": "គ្មានការទាក់ទង",
        "chart_error": "មិនអាចបង្កើតក្រាហ្វបាន (បញ្ហាទិន្នន័យ)",
        "backup_info": "Backup ប្រើ Streamlit Secrets: GITHUB_TOKEN / GITHUB_REPO / GITHUB_USERNAME",
        "backup_success": "Backup ជោគជ័យ",
        "backup_failed": "Backup បរាជ័យ: ",
        "export_excel": "ចេញ Excel",
        "owner_export": "ចេញនូវអតិថិជនរបស់អ្នកទទួលខុសត្រូវ",
        "customer_details": "ព័ត៌មានលម្អិតអតិថិជន",
        "created_at": "បានបង្កើតនៅ",
        "action_logs": "កំណត់ហេតុ",
        "add_user": "បានបន្ថែមអ្នកប្រើ",
        "reset_password": "បានកំណត់ពាក្យសម្ងាត់ឡើងវិញ",
        "delete_user": "បានលុបអ្នកប្រើ",
        "user_added": "បានបន្ថែមអ្នកប្រើ",
        "password_reset": "បានកំណត់ពាក្យសម្ងាត់ឡើងវិញ",
        "user_deleted": "បានលុបអ្នកប្រើ",
        "translations_saved": "បានរក្សាការបកប្រែ",
        "edit_customer_label": "កែព័ត៌មានអតិថិជន",
        "no_permission": "គ្មានសិទ្ធិ",
    },
    "Vietnamese": {
        "language_label": "Chọn ngôn ngữ",
        "menu_navigation": "Điều hướng",
        "menu_dashboard": "📊 Dashboard",
        "menu_customers": "👥 Khách hàng",
        "menu_customers_all": "Tất cả khách hàng",
        "menu_customers_add": "Thêm khách hàng",
        "menu_followups": "📝 Theo dõi",
        "menu_followups_today": "Hôm nay",
        "menu_followups_all": "Tất cả",
        "menu_backup": "💾 Sao lưu GitHub",
        "menu_settings": "⚙ Cài đặt",
        "menu_users": "Quản lý người dùng",
        "menu_translations": "Bản dịch",
        "menu_logs": "Nhật ký",
        "login_title": "Đăng nhập",
        "username": "Tên đăng nhập",
        "password": "Mật khẩu",
        "btn_login": "Đăng nhập",
        "btn_logout": "Đăng xuất",
        "no_data": "Không có dữ liệu",
        "add_customer": "Thêm khách hàng",
        "submit": "Gửi",
        "all_customers": "Tất cả khách hàng",
        "search_owner": "Tìm theo phụ trách chính",
        "input_customer_id": "Nhập ID khách hàng",
        "edit_customer": "Chỉnh sửa khách hàng",
        "delete_customer": "Xóa khách hàng",
        "confirm_delete": "Xác nhận xóa khách hàng này",
        "followup_note": "Ghi chú",
        "next_action": "Hành động tiếp theo",
        "followup_added": "Đã thêm ghi chú",
        "level_pie": "Tỷ lệ cấp độ",
        "trend": "Xu hướng giao dịch",
        "no_deal": "Chưa có giao dịch",
        "chart_error": "Không thể tạo biểu đồ (lỗi dữ liệu)",
        "backup_info": "Sao lưu dùng Streamlit Secrets: GITHUB_TOKEN / GITHUB_REPO / GITHUB_USERNAME",
        "backup_success": "Sao lưu thành công",
        "backup_failed": "Sao lưu thất bại: ",
        "export_excel": "Xuất Excel",
        "owner_export": "Xuất danh sách khách hàng phụ trách",
        "customer_details": "Chi tiết khách hàng",
        "created_at": "Ngày tạo",
        "action_logs": "Nhật ký hành động",
        "add_user": "Thêm người dùng",
        "reset_password": "Đặt lại mật khẩu",
        "delete_user": "Xóa người dùng",
        "user_added": "Đã thêm người dùng",
        "password_reset": "Đã đặt lại mật khẩu",
        "user_deleted": "Đã xóa người dùng",
        "translations_saved": "Đã lưu bản dịch",
        "edit_customer_label": "Chỉnh sửa thông tin khách hàng",
        "no_permission": "Không có quyền",
    },
}

# ------------- 语言工具 -------------
LANG_KEYS = ["中文", "English", "Indonesian", "Khmer", "Vietnamese"]
if "lang" not in st.session_state:
    st.session_state["lang"] = "中文"
if st.session_state["lang"] not in LANG_KEYS:
    st.session_state["lang"] = "中文"


def t(key: str) -> str:
    lang = st.session_state.get("lang", "中文")
    return TRANSLATIONS.get(lang, {}).get(key, key)

# ------------- 辅助函数 -------------
def df_to_excel_bytes(df: pd.DataFrame) -> bytes:
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="sheet1")
    return buf.getvalue()

# ------------- Sidebar：语言 + 菜单（B 结构） -------------
with st.sidebar:
    st.markdown(f"### {t('menu_navigation')}")
    # 语言选择
    lang_index = LANG_KEYS.index(st.session_state.get("lang", "中文")) if st.session_state.get("lang", "中文") in LANG_KEYS else 0
    lang_choice = st.selectbox(t("language_label"), options=LANG_KEYS, index=lang_index)
    if lang_choice != st.session_state.get("lang"):
        st.session_state["lang"] = lang_choice
        st.rerun()

    st.markdown("---")
    # 主菜单
    st.session_state["main_select"] = st.radio("", [t("menu_dashboard"), t("menu_customers"), t("menu_followups"), t("menu_backup"), t("menu_settings")])
    # 子菜单
    if st.session_state["main_select"] == t("menu_customers"):
        st.session_state["sub_select"] = st.selectbox("", [t("menu_customers_all"), t("menu_customers_add")])
    elif st.session_state["main_select"] == t("menu_followups"):
        st.session_state["sub_select"] = st.selectbox("", [t("menu_followups_today"), t("menu_followups_all")])
    elif st.session_state["main_select"] == t("menu_settings"):
        st.session_state["sub_select"] = st.selectbox("", [t("menu_users"), t("menu_translations"), t("menu_logs")])
    else:
        st.session_state["sub_select"] = None

    st.markdown("---")
    if st.session_state.get("username"):
        st.markdown(f"**👤 {st.session_state.get('username')} ({st.session_state.get('role')})**")
        if st.button(t("btn_logout")):
            lang_keep = st.session_state.get("lang", "中文")
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.session_state["lang"] = lang_keep
            st.rerun()

# ------------- 页面实现 -------------
def page_dashboard():
    st.title(t("menu_dashboard"))
    df = customers.list_customers_df()
    if df.empty:
        st.info(t("no_data"))
        return

    total = len(df)
    owners = df["main_owner"].nunique() if "main_owner" in df.columns else 0
    deals = df[df["progress"] == "已成交"].shape[0] if "progress" in df.columns else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("Total", total)
    c2.metric("Owners", owners)
    c3.metric("Deals", deals)

    st.subheader(t("level_pie"))
    try:
        pie = alt.Chart(df).mark_arc().encode(theta=alt.Theta(field="id", aggregate="count"), color="level:N")
        st.altair_chart(pie, use_container_width=True)
    except Exception:
        st.info(t("chart_error"))

    st.subheader("Country distribution / 国家分布")
    try:
        dfc = df.groupby("country").size().reset_index(name="count").sort_values("count", ascending=False).head(20)
        bar = alt.Chart(dfc).mark_bar().encode(x="country:N", y="count:Q")
        st.altair_chart(bar, use_container_width=True)
    except Exception:
        st.info(t("chart_error"))

    st.subheader(t("trend"))
    try:
        df_deal = df[df["progress"] == "已成交"].copy()
        if not df_deal.empty and "created_at" in df_deal.columns:
            df_deal["date"] = pd.to_datetime(df_deal["created_at"], errors="coerce").dt.date
            trend = df_deal.groupby("date").size().reset_index(name="count")
            line = alt.Chart(trend).mark_line().encode(x="date:T", y="count:Q")
            st.altair_chart(line, use_container_width=True)
        else:
            st.info(t("no_deal"))
    except Exception:
        st.info(t("chart_error"))

def page_customers_list():
    st.title(t("menu_customers"))
    df = customers.list_customers_df()
    if df.empty:
        st.info(t("no_data"))
        return

    if st.session_state.get("role") != "admin":
        me = st.session_state.get("username")
        if "main_owner" in df.columns:
            df = df[df["main_owner"] == me]

    st.dataframe(df, use_container_width=True)

    owner = st.text_input(t("search_owner"))
    if owner:
        df2 = df[df["main_owner"] == owner]
        st.dataframe(df2, use_container_width=True)

    if st.button(t("owner_export")):
        buf = df_to_excel_bytes(df)
        st.download_button(label=t("export_excel"), data=buf, file_name="customers.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.markdown("---")
    st.subheader(t("customer_details"))
    cid = st.text_input(t("input_customer_id"))
    if cid:
        cust = customers.get_customer(cid)
        if not cust:
            st.error(t("no_data"))
        else:
            st.json(cust)
            fu = customers.list_followups_df(cid)
            st.subheader("Followups")
            st.dataframe(fu, use_container_width=True)

            with st.form("add_followup_detail"):
                note = st.text_area(t("followup_note"))
                na = st.text_input(t("next_action"))
                if st.form_submit_button(t("submit")):
                    customers.add_followup(cid, st.session_state.get("username","system"), note, na)
                    st.success(t("followup_added"))
                    st.rerun()

            if st.checkbox(t("edit_customer_label")):
                exist = dict(cust)
                with st.form(f"editcust_{cid}"):
                    for fld in ["name","whatsapp","line","telegram","country","city","age","job","income","marital_status","deal_amount","level","progress","main_owner","assistant","notes"]:
                        cur = exist.get(fld,"")
                        if fld == "age":
                            val = st.number_input(fld, value=int(cur) if cur not in [None,""] else 0)
                            exist[fld] = val
                        elif fld == "deal_amount":
                            val = st.number_input(fld, value=float(cur) if cur not in [None,""] else 0.0)
                            exist[fld] = val
                        else:
                            exist[fld] = st.text_input(fld, value=str(cur))
                    if st.form_submit_button(t("submit")):
                        customers.update_customer(cid, exist, operator=st.session_state.get("username","system"))
                        st.success("已更新")
                        st.rerun()

            if st.checkbox(t("confirm_delete")):
                if st.form_submit_button(t("delete_customer")):
                    customers.delete_customer(cid, operator=st.session_state.get("username","system"))
                    st.success("已删除")
                    st.rerun()

def page_customers_add():
    st.title(t("add_customer"))
    with st.form("form_add_customer"):
        rec = {}
        rec["name"] = st.text_input("客户名称")
        rec["whatsapp"] = st.text_input("Whatsapp")
        rec["line"] = st.text_input("Line")
        rec["telegram"] = st.text_input("Telegram")
        rec["country"] = st.text_input("国家")
        rec["city"] = st.text_input("城市")
        rec["age"] = st.number_input("年龄", 0, 120)
        rec["job"] = st.text_input("工作")
        rec["income"] = st.text_input("薪资水平")
        rec["marital_status"] = st.selectbox("感情状态", ["单身","已婚","离异","丧偶"])
        rec["deal_amount"] = st.number_input("成交金额", 0.0)
        rec["level"] = st.selectbox("客户等级", ["普通","重要","VIP"])
        rec["progress"] = st.selectbox("跟进状态", ["待联系","洽谈中","已成交","流失"])
        rec["main_owner"] = st.text_input("主要负责人")
        rec["assistant"] = st.text_input("辅助人员")
        rec["notes"] = st.text_area("备注")
        rec["operator"] = st.session_state.get("username","system")
        if st.form_submit_button(t("submit")):
            cid = customers.insert_customer(rec)
            st.success(f"{t('add_customer')}：{cid}")
            st.rerun()

def page_followups_today():
    st.title(t("menu_followups") + " - " + t("menu_followups_today"))
    df_cust = customers.list_customers_df()
    if df_cust.empty:
        st.info(t("no_data"))
        return
    list_fu = []
    for cid in df_cust['id'].tolist():
        fu = customers.list_followups_df(cid)
        if fu is not None and not fu.empty:
            list_fu.append(fu)
    if not list_fu:
        st.info(t("no_data"))
        return
    df_all = pd.concat(list_fu, ignore_index=True)
    df_all['created_at'] = pd.to_datetime(df_all['created_at'], errors='coerce')
    cutoff = datetime.utcnow() - timedelta(days=1)
    df_show = df_all[df_all['created_at'] >= cutoff]
    if df_show.empty:
        st.info(t("no_data"))
    else:
        st.dataframe(df_show.sort_values("created_at", ascending=False), use_container_width=True)

def page_followups_all():
    st.title(t("menu_followups") + " - " + t("menu_followups_all"))
    df_cust = customers.list_customers_df()
    if df_cust.empty:
        st.info(t("no_data"))
        return
    list_fu = []
    for cid in df_cust['id'].tolist():
        fu = customers.list_followups_df(cid)
        if fu is not None and not fu.empty:
            list_fu.append(fu)
    if not list_fu:
        st.info(t("no_data"))
        return
    df_all = pd.concat(list_fu, ignore_index=True)
    st.dataframe(df_all.sort_values("created_at", ascending=False), use_container_width=True)
    if st.button(t("export_excel")):
        b = df_to_excel_bytes(df_all)
        st.download_button(label=t("export_excel"), data=b, file_name="followups.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

def page_backup_admin():
    st.title(t("menu_backup"))
    st.info(t("backup_info"))
    if st.button("Run backup"):
        ok, msg = backup.backup_db_to_github(st.secrets, actor=st.session_state.get("username","system"))
        if ok:
            st.success(t("backup_success"))
        else:
            st.error(t("backup_failed") + str(msg))

def page_users_admin():
    if st.session_state.get("role") != "admin":
        st.warning(t("no_permission"))
        return
    st.title(t("menu_users"))
    df = auth.list_users()
    st.dataframe(df, use_container_width=True)

    st.subheader(t("add_user"))
    with st.form("form_add_user"):
        u = st.text_input("用户名")
        p = st.text_input("密码")
        r = st.selectbox("角色", ["user","admin"])
        lang_sel = st.selectbox("默认语言", options=LANG_KEYS := LANG_KEYS if 'LANG_KEYS' in globals() else ["中文","English","Indonesian","Khmer","Vietnamese"], index=0)
        if st.form_submit_button(t("submit")):
            auth.add_user(u, p, r, lang_sel)
            st.success(t("user_added"))
            st.rerun()

    st.subheader(t("reset_password"))
    with st.form("form_reset_pass"):
        ru = st.text_input("用户名（重置）")
        rp = st.text_input("新密码")
        if st.form_submit_button(t("submit")):
            auth.reset_password(ru, rp)
            st.success(t("password_reset"))

    st.subheader(t("delete_user"))
    du = st.text_input("要删除的用户名")
    if st.button(t("delete_user")):
        auth.delete_user(du)
        st.success(t("user_deleted"))
        st.rerun()

def page_translations_admin():
    if st.session_state.get("role") != "admin":
        st.warning(t("no_permission"))
        return
    st.title(t("menu_translations"))
    current = translate.load_translations()
    st.subheader("当前翻译 JSON：")
    st.json(current)
    new = st.text_area("编辑翻译 JSON（格式必须正确）", value=str(current), height=300)
    if st.button("保存翻译"):
        try:
            obj = eval(new)
            translate.save_translations(obj)
            st.success(t("translations_saved"))
            st.rerun()
        except Exception as e:
            st.error(str(e))

def page_logs_admin():
    if st.session_state.get("role") != "admin":
        st.warning(t("no_permission"))
        return
    st.title(t("menu_logs"))
    df = logs.recent_actions(1000)
    st.dataframe(df, use_container_width=True)

# ------------- 路由 -------------
def route():
    main = st.session_state.get("main_select", t("menu_dashboard"))
    sub = st.session_state.get("sub_select", None)
    if main == t("menu_dashboard"):
        page_dashboard()
    elif main == t("menu_customers"):
        if sub == t("menu_customers_add"):
            page_customers_add()
        else:
            page_customers_list()
    elif main == t("menu_followups"):
        if sub == t("menu_followups_today"):
            page_followups_today()
        else:
            page_followups_all()
    elif main == t("menu_backup"):
        page_backup_admin()
    elif main == t("menu_settings"):
        # admin subpages through sub_select
        if sub == t("menu_users"):
            page_users_admin()
        elif sub == t("menu_translations"):
            page_translations_admin()
        elif sub == t("menu_logs"):
            page_logs_admin()
        else:
            st.info("Select setting item")
    else:
        st.info("Unknown page")

# ------------- 主入口 -------------
def main():
    # 如果未登录显示登录页
    if "username" not in st.session_state:
        st.title(PAGE_TITLE)
        st.subheader(t("login_title"))
        username = st.text_input(t("username"))
        password = st.text_input(t("password"), type="password")
        if st.button(t("btn_login")):
            info = auth.authenticate(username.strip(), password.strip())
            if info:
                st.session_state["username"] = info["username"]
                st.session_state["role"] = info.get("role", "user")
                user_lang = info.get("language")
                if user_lang in LANG_KEYS:
                    st.session_state["lang"] = user_lang
                st.rerun()
            else:
                st.error("用户名或密码错误")
        return

    # 已登录 -> 路由页面
    route()

if __name__ == "__main__":
    main()
