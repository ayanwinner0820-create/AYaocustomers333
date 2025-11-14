# app.py — 完整版本（多语言、菜单 B、Dashboard 图表、客户管理、跟进、备份、管理员）
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
from io import BytesIO

from config import PAGE_TITLE, PAGE_ICON, THEME_COLOR, LANG_OPTIONS
from db import init_db
import auth
import customers
import logs
import translate
import backup

# --------- 初始化与页面配置 ----------
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)
init_db()

# 加载 translations（从 translate.py -> translations.json）
TRANSLATIONS = translate.load_translations()

# 内置默认五语覆盖项（尽量减少“未翻译”情况）
DEFAULT_I18N = {
    "zh": {
        "login_title": "登录系统",
        "username": "用户名",
        "password": "密码",
        "btn_login": "登录",
        "btn_logout": "退出登录",
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
        "customers_title": "客户管理",
        "add_customer": "添加客户",
        "submit": "提交",
        "all_customers": "所有客户",
        "no_data": "暂无数据",
        "search_owner": "按主要负责人搜索",
        "input_customer_id": "输入客户 ID",
        "edit_customer": "编辑客户",
        "delete_customer": "删除客户",
        "confirm_delete": "确认删除该客户",
        "followup_title": "客户跟进",
        "followup_note": "跟进内容",
        "next_action": "下一步动作",
        "followup_added": "跟进记录已创建",
        "charts_title": "负责人数据报表",
        "select_owner": "选择负责人",
        "time_range": "时间区间",
        "data_count": "当前数据量：",
        "level_pie": "客户等级占比",
        "trend": "成交趋势",
        "no_deal": "暂无成交数据",
        "chart_error": "无法生成图表（数据问题）",
        "user_added": "用户已创建",
        "password_reset": "密码已重置",
        "user_deleted": "用户已删除",
        "backup_info": "自动备份使用 Streamlit Secrets: GITHUB_TOKEN / GITHUB_REPO / GITHUB_USERNAME",
        "backup_success": "备份成功",
        "backup_failed": "备份失败：",
        "translations_saved": "翻译已保存",
        "export_excel": "导出 Excel",
        "owner_export": "导出负责人负责的客户（Excel）",
        "customer_details": "客户详情",
        "created_at": "创建时间",
        "action_logs": "操作日志",
    },
    "en": {
        "login_title": "Login",
        "username": "Username",
        "password": "Password",
        "btn_login": "Login",
        "btn_logout": "Logout",
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
        "customers_title": "Customers",
        "add_customer": "Add Customer",
        "submit": "Submit",
        "all_customers": "All Customers",
        "no_data": "No data",
        "search_owner": "Search by main owner",
        "input_customer_id": "Input customer ID",
        "edit_customer": "Edit customer",
        "delete_customer": "Delete customer",
        "confirm_delete": "Confirm delete this customer",
        "followup_title": "Customer Followups",
        "followup_note": "Followup note",
        "next_action": "Next action",
        "followup_added": "Followup added",
        "charts_title": "Owner Reports",
        "select_owner": "Select owner",
        "time_range": "Time range",
        "data_count": "Count:",
        "level_pie": "Level distribution",
        "trend": "Deal trend",
        "no_deal": "No deals",
        "chart_error": "Cannot generate chart (data issue)",
        "user_added": "User added",
        "password_reset": "Password reset",
        "user_deleted": "User deleted",
        "backup_info": "Backups use Streamlit Secrets: GITHUB_TOKEN / GITHUB_REPO / GITHUB_USERNAME",
        "backup_success": "Backup success",
        "backup_failed": "Backup failed: ",
        "translations_saved": "Translations saved",
        "export_excel": "Export Excel",
        "owner_export": "Export owner's customers (Excel)",
        "customer_details": "Customer details",
        "created_at": "Created at",
        "action_logs": "Action Logs",
    },
    "id": {  # Bahasa Indonesia (basic)
        "login_title": "Masuk",
        "username": "Nama Pengguna",
        "password": "Kata Sandi",
        "btn_login": "Masuk",
        "btn_logout": "Keluar",
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
        "customers_title": "Manajemen Pelanggan",
        "add_customer": "Tambah Pelanggan",
        "submit": "Kirim",
        "all_customers": "Semua Pelanggan",
        "no_data": "Tidak ada data",
        "search_owner": "Cari berdasarkan penanggung jawab",
        "input_customer_id": "Masukkan ID pelanggan",
        "edit_customer": "Edit pelanggan",
        "delete_customer": "Hapus pelanggan",
        "confirm_delete": "Konfirmasi hapus pelanggan ini",
        "followup_title": "Tindak lanjut pelanggan",
        "followup_note": "Catatan tindak lanjut",
        "next_action": "Tindakan selanjutnya",
        "followup_added": "Tindak lanjut ditambahkan",
        "charts_title": "Laporan Penanggung Jawab",
        "select_owner": "Pilih penanggung jawab",
        "time_range": "Rentang waktu",
        "data_count": "Jumlah data:",
        "level_pie": "Distribusi level",
        "trend": "Tren transaksi",
        "no_deal": "Belum ada transaksi",
        "chart_error": "Tidak dapat membuat grafik (masalah data)",
        "user_added": "Pengguna ditambahkan",
        "password_reset": "Kata sandi direset",
        "user_deleted": "Pengguna dihapus",
        "backup_info": "Cadangan menggunakan Streamlit Secrets: GITHUB_TOKEN / GITHUB_REPO / GITHUB_USERNAME",
        "backup_success": "Cadangan berhasil",
        "backup_failed": "Cadangan gagal: ",
        "translations_saved": "Terjemahan tersimpan",
        "export_excel": "Ekspor Excel",
        "owner_export": "Ekspor pelanggan penanggung jawab (Excel)",
        "customer_details": "Detail pelanggan",
        "created_at": "Dibuat pada",
        "action_logs": "Log tindakan",
    },
    "km": {  # Khmer (simple)
        "login_title": "ចូលប្រព័ន្ធ",
        "username": "ឈ្មោះអ្នកប្រើ",
        "password": "ពាក្យសម្ងាត់",
        "btn_login": "ចូល",
        "btn_logout": "ចាកចេញ",
        "menu_navigation": "ការរុករក",
        "menu_dashboard": "📊 Dashboard",
        "menu_customers": "👥 អតិថិជន",
        "menu_customers_all": "អតិថិជនទាំងអស់",
        "menu_customers_add": "បញ្ចូលអតិថិជន",
        "menu_followups": "📝 ដំណើរការ",
        "menu_followups_today": "ថ្ងៃនេះ",
        "menu_followups_all": "ទាំងអស់",
        "menu_backup": "💾Backup",
        "menu_settings": "⚙ ការកំណត់",
        "menu_users": "គ្រប់គ្រងអ្នកប្រើ",
        "menu_translations": "ការបកប្រែ",
        "menu_logs": "កំណត់ហេតុ",
        "customers_title": "គ្រប់គ្រងអតិថិជន",
        "add_customer": "បន្ថែមអតិថិជន",
        "submit": "បញ្ជូន",
        "all_customers": "អតិថិជនទាំងអស់",
        "no_data": "គ្មានទិន្នន័យ",
        "search_owner": "ស្វែងរកតាមអ្នកទទួលខុសត្រូវ",
        "input_customer_id": "បញ្ចូលលេខសម្គាល់អតិថិជន",
        "edit_customer": "កែសម្រួលអតិថិជន",
        "delete_customer": "លុបអតិថិជន",
        "confirm_delete": "បញ្ជាក់លុបអតិថិជននេះ",
        "followup_title": "ដំណើរការអតិថិជន",
        "followup_note": "កំណត់សម្គាល់",
        "next_action": "សកម្មភាពបន្ទាប់",
        "followup_added": "បានបន្ថែមកំណត់ហេតុ",
        "charts_title": "របាយការណ៍",
        "select_owner": "ជ្រើសអ្នកទទួលខុសត្រូវ",
        "time_range": "ចន្លោះពេល",
        "data_count": "ចំនួនទិន្នន័យ:",
        "level_pie": "ចែកចាយកម្រិត",
        "trend": "និន្នាការ",
        "no_deal": "គ្មានការទាក់ទង",
        "chart_error": "មិនអាចបង្កើតក្រាហ្វបាន (បញ្ហាទិន្នន័យ)",
        "user_added": "បានបន្ថែមអ្នកប្រើ",
        "password_reset": "បានកំណត់ពាក្យសម្ងាត់ឡើងវិញ",
        "user_deleted": "បានលុបអ្នកប្រើ",
        "backup_info": "Backup ប្រើ Streamlit Secrets: GITHUB_TOKEN / GITHUB_REPO / GITHUB_USERNAME",
        "backup_success": "Backup ជោគជ័យ",
        "backup_failed": "Backup បរាជ័យ: ",
        "translations_saved": "បានរក្សាការបកប្រែ",
        "export_excel": "ចេញ Excel",
        "owner_export": "ចេញនូវអតិថិជនរបស់អ្នកទទួលខុសត្រូវ",
        "customer_details": "ព័ត៌មានលម្អិតអតិថិជន",
        "created_at": "បានបង្កើតនៅ",
        "action_logs": "កំណត់ហេតុអន្តរាគមន៍",
    },
    "vi": {
        "login_title": "Đăng nhập",
        "username": "Tên đăng nhập",
        "password": "Mật khẩu",
        "btn_login": "Đăng nhập",
        "btn_logout": "Đăng xuất",
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
        "customers_title": "Quản lý khách hàng",
        "add_customer": "Thêm khách hàng",
        "submit": "Gửi",
        "all_customers": "Tất cả khách hàng",
        "no_data": "Không có dữ liệu",
        "search_owner": "Tìm theo phụ trách chính",
        "input_customer_id": "Nhập ID khách hàng",
        "edit_customer": "Chỉnh sửa khách hàng",
        "delete_customer": "Xóa khách hàng",
        "confirm_delete": "Xác nhận xóa khách hàng này",
        "followup_title": "Theo dõi khách hàng",
        "followup_note": "Ghi chú theo dõi",
        "next_action": "Hành động tiếp theo",
        "followup_added": "Đã thêm theo dõi",
        "charts_title": "Báo cáo theo phụ trách",
        "select_owner": "Chọn phụ trách",
        "time_range": "Khoảng thời gian",
        "data_count": "Số lượng:",
        "level_pie": "Tỷ lệ mức độ",
        "trend": "Xu hướng giao dịch",
        "no_deal": "Chưa có giao dịch",
        "chart_error": "Không thể tạo biểu đồ (lỗi dữ liệu)",
        "user_added": "Đã thêm người dùng",
        "password_reset": "Đã đặt lại mật khẩu",
        "user_deleted": "Đã xóa người dùng",
        "backup_info": "Sao lưu dùng Streamlit Secrets: GITHUB_TOKEN / GITHUB_REPO / GITHUB_USERNAME",
        "backup_success": "Sao lưu thành công",
        "backup_failed": "Sao lưu thất bại: ",
        "translations_saved": "Đã lưu bản dịch",
        "export_excel": "Xuất Excel",
        "owner_export": "Xuất danh sách khách hàng phụ trách",
        "customer_details": "Chi tiết khách hàng",
        "created_at": "Ngày tạo",
        "action_logs": "Nhật ký hành động",
    },
}

# 合并 TRANSLATIONS（外部文件优先，缺少项用内置）
def get_translation(lang_code):
    # TRANSLATIONS expected to be like {"中文": {...}, "English": {...}, ...} or language codes.
    # We'll normalize keys to language codes if possible.
    # Try common keys first
    if isinstance(TRANSLATIONS, dict):
        # if keys appear as language names (Chinese/English), map to codes
        if all(k in ["中文", "English", "Bahasa Indonesia", "ភាសាខ្មែរ", "Tiếng Việt"] for k in TRANSLATIONS.keys()):
            mapping = {
                "中文": "zh",
                "English": "en",
                "Bahasa Indonesia": "id",
                "ភាសាខ្មែរ": "km",
                "Tiếng Việt": "vi"
            }
            mapped = {}
            for k, v in TRANSLATIONS.items():
                code = mapping.get(k, k)
                mapped[code] = v
            return mapped.get(lang_code, DEFAULT_I18N.get(lang_code, {}))
        # else maybe already using codes:
        if lang_code in TRANSLATIONS:
            return TRANSLATIONS[lang_code]
    return DEFAULT_I18N.get(lang_code, {})

# 语言选择默认值 set
if "lang" not in st.session_state:
    # try to use user's default in session or fallback to zh
    st.session_state["lang"] = "zh"

# helper t() using merged translations
def t(key):
    lang_code = st.session_state.get("lang", "zh")
    tr = get_translation(lang_code)
    return tr.get(key, DEFAULT_I18N.get(lang_code, {}).get(key, key))

# --- Sidebar language selector and menu (menu structure B) ---
with st.sidebar:
    st.markdown(f"## {t('menu_navigation')}")
    # language selectbox showing friendly names
    lang_keys = ["zh", "en", "id", "km", "vi"]
    lang_labels = [LANG_OPTIONS.get("中文","中文") if False else None]  # placeholder to avoid lint
    # build display list
    labels = [ "中文", "English", "Bahasa Indonesia", "ភាសាខ្មែរ", "Tiếng Việt" ]
    sel = st.selectbox(t("language") if t("language") else "Language", options=lang_keys,
                       format_func=lambda x: {"zh":"中文","en":"English","id":"Bahasa Indonesia","km":"ភាសាខ្មែរ","vi":"Tiếng Việt"}.get(x, x),
                       index=lang_keys.index(st.session_state["lang"]))
    if sel != st.session_state["lang"]:
        st.session_state["lang"] = sel
        st.rerun()

    st.sidebar.markdown("---")
    # Main grouped menu (B)
    main_section = st.radio("",
                            [t("menu_dashboard"),
                             t("menu_customers"),
                             t("menu_followups"),
                             t("menu_backup"),
                             t("menu_settings")],
                            index=0)

    # If Customers selected, show subpages
    subpage = None
    if main_section == t("menu_customers"):
        subpage = st.selectbox("", [t("menu_customers_all"), t("menu_customers_add")])
    elif main_section == t("menu_followups"):
        subpage = st.selectbox("", [t("menu_followups_today"), t("menu_followups_all")])
    elif main_section == t("menu_settings"):
        subpage = st.selectbox("", [t("menu_users"), t("menu_translations"), t("menu_logs")])
    else:
        subpage = None

    st.sidebar.markdown("---")
    if st.session_state.get("username"):
        st.sidebar.write(f"👤 {st.session_state.get('username')}  ({st.session_state.get('role')})")
        if st.button(t("btn_logout")):
            # clear session except language
            lang = st.session_state.get("lang", "zh")
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.session_state["lang"] = lang
            st.rerun()

# ---------- Helper utilities ----------
def export_df_to_excel(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="customers")
        writer.save()
    return buffer.getvalue()

# ---------- Page: Dashboard ----------
def page_dashboard():
    st.title(t("menu_dashboard"))
    df = customers.list_customers_df()
    if df.empty:
        st.info(t("no_data"))
        return

    # show quick stats
    total = len(df)
    owners = df["main_owner"].nunique() if "main_owner" in df.columns else 0
    deals = df[df["progress"] == "已成交"].shape[0] if "progress" in df.columns else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total", total)
    col2.metric("Owners", owners)
    col3.metric("Deals", deals)

    # pie chart: level distribution
    st.subheader(t("level_pie"))
    try:
        c1 = alt.Chart(df).mark_arc().encode(
            theta=alt.Theta(field="id", aggregate="count"),
            color="level:N"
        )
        st.altair_chart(c1, use_container_width=True)
    except Exception:
        st.info(t("chart_error"))

    # bar chart: customers by country (top 10)
    st.subheader("Country / 国家分布")
    try:
        dfc = df.groupby("country").size().reset_index(name="count").sort_values("count", ascending=False).head(10)
        bar = alt.Chart(dfc).mark_bar().encode(x="country:N", y="count:Q")
        st.altair_chart(bar, use_container_width=True)
    except Exception:
        st.info(t("chart_error"))

    # deals over time
    st.subheader(t("trend"))
    try:
        df_deals = df[df["progress"] == "已成交"].copy()
        if not df_deals.empty and "created_at" in df_deals.columns:
            df_deals["date"] = pd.to_datetime(df_deals["created_at"], errors="coerce").dt.date
            trend = df_deals.groupby("date").size().reset_index(name="count")
            line = alt.Chart(trend).mark_line().encode(x="date:T", y="count:Q")
            st.altair_chart(line, use_container_width=True)
        else:
            st.info(t("no_deal"))
    except Exception:
        st.info(t("chart_error"))

# ---------- Page: Customers (list / add / edit) ----------
def page_customers_all():
    st.title(t("customers_title"))
    df = customers.list_customers_df()
    if df.empty:
        st.info(t("no_data"))
    else:
        # Permissions: non-admin sees only own customers
        if st.session_state.get("role") != "admin":
            user = st.session_state.get("username")
            df = df[(df["main_owner"] == user) | (df["assistant"].fillna("").str.contains(user))]
        st.dataframe(df, use_container_width=True)

        # export
        if st.button(t("export_excel")):
            b = export_df_to_excel(df)
            st.download_button(label=t("export_excel"), data=b, file_name="customers.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.markdown("---")
    st.subheader(t("customer_details"))
    cid = st.text_input(t("input_customer_id"))
    if cid:
        cust = customers.get_customer(cid)
        if not cust:
            st.error(t("no_data"))
        else:
            st.json(cust)
            # followups for this customer
            fu = customers.list_followups_df(cid)
            st.subheader("Followups")
            st.dataframe(fu, use_container_width=True)
            # allow add followup
            with st.form("add_followup_detail"):
                note = st.text_area(t("followup_note"))
                next_action = st.text_input(t("next_action"))
                if st.form_submit_button(t("submit")):
                    customers.add_followup(cid, st.session_state.get("username","system"), note, next_action)
                    st.success(t("followup_added"))
                    st.rerun()

            # edit customer
            if st.checkbox(t("edit_customer")):
                cust_edit = dict(cust)
                with st.form(f"edit_form_{cid}"):
                    for field in ["name","whatsapp","line","telegram","country","city","age","job","income","marital_status","deal_amount","level","progress","main_owner","assistant","notes"]:
                        val = cust_edit.get(field, "")
                        # handle number fields display
                        if field in ["age"]:
                            newv = st.number_input(field, value=int(val) if val not in [None,""] else 0)
                            cust_edit[field] = newv
                        elif field in ["deal_amount"]:
                            newv = st.number_input(field, value=float(val) if val not in [None,""] else 0.0)
                            cust_edit[field] = newv
                        else:
                            cust_edit[field] = st.text_input(field, value=str(val))
                    if st.form_submit_button(t("submit_update") if "submit_update" in get_translation(st.session_state.get("lang","zh")) else "提交"):
                        customers.update_customer(cid, cust_edit, operator=st.session_state.get("username","system"))
                        st.success(t("updated") if "updated" in get_translation(st.session_state.get("lang","zh")) else "已更新")
                        st.rerun()

            # delete
            if st.checkbox(t("confirm_delete")):
                if st.button(t("delete_customer")):
                    customers.delete_customer(cid, operator=st.session_state.get("username","system"))
                    st.success(t("deleted") if "deleted" in get_translation(st.session_state.get("lang","zh")) else "已删除")
                    st.rerun()

def page_customers_add():
    st.title(t("add_customer"))
    with st.form("add_customer_form"):
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
            st.success(f"{t('user_added')} {cid}")
            st.rerun()

# ---------- Page: Followups ----------
def page_followups_today():
    st.title(t("menu_followups") + " — " + t("menu_followups_today"))
    df = customers.list_followups_df_all() if hasattr(customers, "list_followups_df_all") else pd.DataFrame()
    # fallback: show recent followups via action logs or followups table
    conn = None
    try:
        # try to collect from customers.list_followups_df for recent customers
        all_followups = []
        # if module provides list_followups_all, use it
        if hasattr(customers, "list_followups_all"):
            df = customers.list_followups_all()
            st.dataframe(df)
            return
        else:
            # try to query followups by scanning some customers (may be inefficient)
            df_cust = customers.list_customers_df()
            recent = []
            for cid in df_cust['id'].head(200).tolist() if not df_cust.empty else []:
                fu = customers.list_followups_df(cid)
                if not fu.empty:
                    recent.append(fu)
            if recent:
                df_fu = pd.concat(recent, ignore_index=True)
                df_fu['created_at'] = pd.to_datetime(df_fu['created_at'], errors='coerce')
                cutoff = datetime.utcnow() - timedelta(days=1)
                df_fu = df_fu[df_fu['created_at'] >= pd.to_datetime(cutoff)]
                st.dataframe(df_fu)
            else:
                st.info(t("no_data"))
    except Exception:
        st.info(t("no_data"))

def page_followups_all():
    st.title(t("menu_followups") + " — " + t("menu_followups_all"))
    # collect all followups across customers (may be in followups table)
    # try using customers.list_followups_df for known list of customers
    df_cust = customers.list_customers_df()
    if df_cust.empty:
        st.info(t("no_data"))
        return
    all_fu = []
    for cid in df_cust['id'].tolist():
        fu = customers.list_followups_df(cid)
        if not fu.empty:
            all_fu.append(fu)
    if all_fu:
        df_all = pd.concat(all_fu, ignore_index=True)
        st.dataframe(df_all.sort_values("created_at", ascending=False))
        # export
        if st.button(t("export_excel")):
            b = export_df_to_excel(df_all)
            st.download_button(label=t("export_excel"), data=b, file_name="followups.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info(t("no_data"))

# ---------- Page: Backup ----------
def page_backup():
    st.title(t("menu_backup"))
    st.info(t("backup_info"))
    if st.button("Run backup"):
        ok, msg = backup.backup_db_to_github(st.secrets, actor=st.session_state.get("username","system"))
        if ok:
            st.success(t("backup_success"))
        else:
            st.error(t("backup_failed") + str(msg))

# ---------- Page: Settings (admin) ----------
def page_users_admin():
    st.title(t("menu_users"))
    df = auth.list_users()
    st.dataframe(df)
    st.subheader(t("add_user"))
    with st.form("add_user_admin"):
        u = st.text_input("用户名")
        p = st.text_input("密码")
        r = st.selectbox("角色", ["user","admin"])
        lang = st.selectbox("默认语言", ["zh","en","id","km","vi"], format_func=lambda x: {"zh":"中文","en":"English","id":"Bahasa Indonesia","km":"ភាសាខ្មែរ","vi":"Tiếng Việt"}[x])
        if st.form_submit_button(t("submit")):
            auth.add_user(u,p,r,lang)
            st.success(t("user_added"))
            st.rerun()
    st.subheader(t("reset_password"))
    with st.form("reset_pass_admin"):
        u2 = st.text_input("用户名（重置）")
        p2 = st.text_input("新密码")
        if st.form_submit_button(t("submit")):
            auth.reset_password(u2, p2)
            st.success(t("password_reset"))
    st.subheader(t("delete_user"))
    del_u = st.text_input("要删除的用户名")
    if st.button(t("delete_user_button") if "delete_user_button" in DEFAULT_I18N.get("zh",{}) else "删除用户"):
        auth.delete_user(del_u)
        st.success(t("user_deleted"))
        st.rerun()

def page_translations_admin():
    st.title(t("menu_translations"))
    current = translate.load_translations()
    st.subheader("当前翻译（JSON）")
    st.json(current)
    new_text = st.text_area("编辑翻译 JSON（格式必须正确）", value=str(current), height=300)
    if st.button(t("save_json") if "save_json" in get_translation(st.session_state.get("lang","zh")) else "保存"):
        try:
            obj = eval(new_text)
            translate.save_translations(obj)
            st.success(t("translations_saved"))
            st.rerun()
        except Exception as e:
            st.error(str(e))

def page_logs_admin():
    st.title(t("menu_logs"))
    df = logs.recent_actions(1000)
    st.dataframe(df)

# ---------- Router ----------
def router(main_section, subpage):
    if main_section == t("menu_dashboard"):
        page_dashboard()
    elif main_section == t("menu_customers"):
        if subpage == t("menu_customers_add"):
            page_customers_add()
        else:
            page_customers_all()
    elif main_section == t("menu_followups"):
        if subpage == t("menu_followups_today"):
            page_followups_today()
        else:
            page_followups_all()
    elif main_section == t("menu_backup"):
        page_backup()
    elif main_section == t("menu_settings"):
        # show admin subpages only for admin
        if st.session_state.get("role") != "admin":
            st.warning("Admin only")
            return
        if subpage == t("menu_users"):
            page_users_admin()
        elif subpage == t("menu_translations"):
            page_translations_admin()
        elif subpage == t("menu_logs"):
            page_logs_admin()

# ---------- Main ----------
def main():
    # show login if user not logged
    if "username" not in st.session_state:
        # show simplified login box on main area
        st.title(PAGE_TITLE)
        st.write("")  # spacing
        st.write("")  # spacing
        st.subheader(t("login_title"))
        username = st.text_input(t("username"))
        password = st.text_input(t("password"), type="password")
        if st.button(t("btn_login")):
            info = auth.authenticate(username.strip(), password.strip())
            if info:
                st.session_state["username"] = info["username"]
                st.session_state["role"] = info.get("role","user")
                st.session_state["lang"] = info.get("language", st.session_state.get("lang","zh"))
                # optional admin backup on login - commented out to avoid unexpected pushes
                # if st.session_state["role"] == "admin":
                #     backup.backup_db_to_github(st.secrets, actor=st.session_state["username"])
                st.rerun()
            else:
                st.error("用户名或密码错误")
        return

    # if logged in, route based on sidebar selections (we stored main_section and subpage in sidebar above)
    # retrieve sidebar values
    # Note: because sidebar variables are local inside sidebar context, we re-evaluate via session_state if needed.
    # For simplicity, recompute menu selection from UI (we used variables earlier)
    try:
        main_section = main_section  # defined in sidebar scope earlier
    except Exception:
        # fallback: show dashboard
        main_section = t("menu_dashboard")
        subpage_local = None
    # We can read them from query params or from session_state if persisted, but to keep code simple,
    # recreate choices: find which radio option is selected by checking presence in page header - not robust.
    # Instead, we will ask user to click again; simpler: default to dashboard
    # Actually we stored main_section in a local variable during sidebar rendering, then call router()
    # So call router using the last-known from that sidebar render; because Streamlit runs top-to-bottom,
    # the earlier sidebar code defined main_section and subpage in this run, so they exist here.
    try:
        subpage_local = subpage
    except Exception:
        subpage_local = None

    # call the router with the values from sidebar
    router(main_section, subpage_local)


if __name__ == "__main__":
    main()
