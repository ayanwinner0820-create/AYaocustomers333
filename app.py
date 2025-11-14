# app.py — 完整可运行版本
# 依赖：auth.py, customers.py, translate.py, backup.py, logs.py, db.py, config.py 等同目录模块

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

# ---------------------------
# 初始化
# ---------------------------
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide", initial_sidebar_state="expanded")
init_db()  # ensure DB and default admin exist

# load translations (translate.load_translations should return dict keyed by language names)
RAW_TRANSLATIONS = translate.load_translations()

# default i18n fallback structure using your confirmed keys:
DEFAULT_I18N = {
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
    },
    "Indonesian": {},  # will fallback to provided RAW_TRANSLATIONS or DEFAULT_I18N later
    "Khmer": {},
    "Vietnamese": {}
}

# Safely build merged translations mapping: prefer RAW_TRANSLATIONS keys (user-provided),
# fallback to DEFAULT_I18N if missing
def merged_translation_for(lang_key: str):
    # RAW_TRANSLATIONS may be in either language names or codes; user requested keys are these exact strings
    if isinstance(RAW_TRANSLATIONS, dict) and lang_key in RAW_TRANSLATIONS and isinstance(RAW_TRANSLATIONS[lang_key], dict):
        # merge: raw first, then default gaps
        base = DEFAULT_I18N.get(lang_key, {}).copy()
        base.update(RAW_TRANSLATIONS.get(lang_key, {}))
        return base
    # fallback to default
    return DEFAULT_I18N.get(lang_key, {})

# ensure session language exists and is one of the allowed keys
LANG_KEYS = ["中文", "English", "Indonesian", "Khmer", "Vietnamese"]
if "lang" not in st.session_state:
    st.session_state["lang"] = "中文"
# normalize session lang if invalid
if st.session_state["lang"] not in LANG_KEYS:
    st.session_state["lang"] = "中文"

# helper t()
def t(key: str) -> str:
    lang = st.session_state.get("lang", "中文")
    tr = merged_translation_for(lang)
    return tr.get(key, DEFAULT_I18N.get(lang, {}).get(key, key))

# safe excel export
def df_to_excel_bytes(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="sheet1")
    return buffer.getvalue()

# ---------------------------
# Sidebar — Language + Menu (结构 B)
# ---------------------------
with st.sidebar:
    st.markdown(f"### {t('menu_navigation')}")
    # language selector (safe fallback)
    langs = LANG_KEYS
    current = st.session_state.get("lang", "中文")
    if current not in langs:
        current = "中文"
        st.session_state["lang"] = current

    new_lang = st.selectbox(t("language_label"), options=langs, index=langs.index(current))
    if new_lang != st.session_state["lang"]:
        st.session_state["lang"] = new_lang
        st.rerun()

    st.markdown("---")
    # Main grouped menu B
    main_select = st.radio("", [t("menu_dashboard"), t("menu_customers"), t("menu_followups"), t("menu_backup"), t("menu_settings")], index=0)
    # Sub-menu area
    sub_select = None
    if main_select == t("menu_customers"):
        sub_select = st.selectbox("", [t("menu_customers_all"), t("menu_customers_add")])
    elif main_select == t("menu_followups"):
        sub_select = st.selectbox("", [t("menu_followups_today"), t("menu_followups_all")])
    elif main_select == t("menu_settings"):
        # show admin sections; we hide admin-only later in routing
        sub_select = st.selectbox("", [t("menu_users"), t("menu_translations"), t("menu_logs")])
    else:
        sub_select = None

    st.markdown("---")
    # show current user (if any)
    if st.session_state.get("username"):
        st.write(f"👤 {st.session_state.get('username')}  ({st.session_state.get('role')})")
        if st.button(t("btn_logout")):
            # keep language, clear rest
            lang_keep = st.session_state.get("lang", "中文")
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.session_state["lang"] = lang_keep
            st.rerun()

# ---------------------------
# Pages implementation
# ---------------------------

# Dashboard
def page_dashboard():
    st.title(t("menu_dashboard"))
    df = customers.list_customers_df()
    if df.empty:
        st.info(t("no_data"))
        return

    # Quick metrics
    total = len(df)
    owners = df["main_owner"].nunique() if "main_owner" in df.columns else 0
    deals = df[df["progress"] == "已成交"].shape[0] if "progress" in df.columns else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("Total", total)
    c2.metric("Owners", owners)
    c3.metric("Deals", deals)

    # Level pie
    st.subheader(t("level_pie"))
    try:
        pie = alt.Chart(df).mark_arc().encode(theta=alt.Theta(field="id", aggregate="count"), color="level:N")
        st.altair_chart(pie, use_container_width=True)
    except Exception:
        st.info(t("chart_error"))

    # Country bar
    st.subheader("Country distribution / 国家分布")
    try:
        dfc = df.groupby("country").size().reset_index(name="count").sort_values("count", ascending=False).head(20)
        bar = alt.Chart(dfc).mark_bar().encode(x="country:N", y="count:Q")
        st.altair_chart(bar, use_container_width=True)
    except Exception:
        st.info(t("chart_error"))

    # Deal trend
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

# Customers - list
def page_customers_list():
    st.title(t("customers_title") if "customers_title" in merged_translation_for(st.session_state["lang"]) else t("menu_customers"))
    df = customers.list_customers_df()
    if df.empty:
        st.info(t("no_data"))
        return

    # permission: normal user sees only own customers
    if st.session_state.get("role") != "admin":
        me = st.session_state.get("username")
        if "main_owner" in df.columns:
            df = df[df["main_owner"] == me]

    st.dataframe(df, use_container_width=True)

    # owner search
    owner = st.text_input(t("search_owner"))
    if owner:
        df = df[df["main_owner"] == owner]
        st.dataframe(df)

    # export by owner
    if st.button(t("owner_export")):
        # only export allowed customers for user
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
            # followups list
            fu = customers.list_followups_df(cid)
            st.subheader("Followups")
            st.dataframe(fu, use_container_width=True)
            # add followup
            with st.form("add_followup_in_detail"):
                note = st.text_area(t("followup_note"))
                na = st.text_input(t("next_action"))
                if st.form_submit_button(t("submit")):
                    customers.add_followup(cid, st.session_state.get("username","system"), note, na)
                    st.success(t("followup_added"))
                    st.rerun()
            # edit
            if st.checkbox(t("edit_customer")):
                exist = dict(cust)
                with st.form(f"editcust_{cid}"):
                    for fld in ["name","whatsapp","line","telegram","country","city","age","job","income","marital_status","deal_amount","level","progress","main_owner","assistant","notes"]:
                        cur = exist.get(fld,"")
                        if fld in ["age"]:
                            val = st.number_input(fld, value=int(cur) if cur not in [None,""] else 0)
                            exist[fld] = val
                        elif fld in ["deal_amount"]:
                            val = st.number_input(fld, value=float(cur) if cur not in [None,""] else 0.0)
                            exist[fld] = val
                        else:
                            exist[fld] = st.text_input(fld, value=str(cur))
                    if st.form_submit_button(t("submit")):
                        customers.update_customer(cid, exist, operator=st.session_state.get("username","system"))
                        st.success("已更新")
                        st.rerun()
            # delete
            if st.checkbox(t("confirm_delete")):
                if st.button(t("delete_customer")):
                    customers.delete_customer(cid, operator=st.session_state.get("username","system"))
                    st.success("已删除")
                    st.rerun()

# Customers - add
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
            st.success(f"客户已添加：{cid}")
            st.rerun()

# Followups Today
def page_followups_today():
    st.title(t("menu_followups") + " - " + t("menu_followups_today"))
    # We'll collect followups for the last 1 day from followups table
    df_all = []
    df_cust = customers.list_customers_df()
    if df_cust.empty:
        st.info(t("no_data"))
        return
    for cid in df_cust['id'].tolist():
        fu = customers.list_followups_df(cid)
        if not fu.empty:
            df_all.append(fu)
    if not df_all:
        st.info(t("no_data"))
        return
    df_all = pd.concat(df_all, ignore_index=True)
    df_all['created_at'] = pd.to_datetime(df_all['created_at'], errors='coerce')
    cutoff = datetime.utcnow() - timedelta(days=1)
    df_show = df_all[df_all['created_at'] >= cutoff]
    if df_show.empty:
        st.info(t("no_data"))
    else:
        st.dataframe(df_show.sort_values("created_at", ascending=False))

# Followups All
def page_followups_all():
    st.title(t("menu_followups") + " - " + t("menu_followups_all"))
    df_list = []
    df_cust = customers.list_customers_df()
    if df_cust.empty:
        st.info(t("no_data"))
        return
    for cid in df_cust['id'].tolist():
        fu = customers.list_followups_df(cid)
        if not fu.empty:
            df_list.append(fu)
    if not df_list:
        st.info(t("no_data"))
        return
    df_all = pd.concat(df_list, ignore_index=True)
    st.dataframe(df_all.sort_values("created_at", ascending=False), use_container_width=True)
    if st.button(t("export_excel")):
        b = df_to_excel_bytes(df_all)
        st.download_button(label=t("export_excel"), data=b, file_name="followups.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Backup page
def page_backup():
    st.title(t("menu_backup"))
    st.info(t("backup_info"))
    if st.button("Run backup"):
        ok, msg = backup.backup_db_to_github(st.secrets, actor=st.session_state.get("username","system"))
        if ok:
            st.success(t("backup_success"))
        else:
            st.error(t("backup_failed") + str(msg))

# Admin: users
def page_users_admin():
    st.title(t("menu_users"))
    df = auth.list_users()
    st.dataframe(df, use_container_width=True)
    st.subheader(t("add_user"))
    with st.form("form_add_user"):
        u = st.text_input("用户名")
        p = st.text_input("密码")
        r = st.selectbox("角色", ["user","admin"])
        lang = st.selectbox("默认语言", LANG_KEYS := LANG_KEYS if 'LANG_KEYS' in globals() else ["中文","English","Indonesian","Khmer","Vietnamese"], index=0)
        if st.form_submit_button(t("submit")):
            auth.add_user(u, p, r, lang)
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

# Admin: translations
def page_translations_admin():
    st.title(t("menu_translations"))
    data = translate.load_translations()
    st.subheader("当前翻译 JSON：")
    st.json(data, expanded=False)
    new = st.text_area("编辑翻译 JSON（格式必须正确）", value=str(data), height=300)
    if st.button("保存翻译"):
        try:
            obj = eval(new)
            translate.save_translations(obj)
            st.success(t("translations_saved"))
            st.rerun()
        except Exception as e:
            st.error(str(e))

# Admin: logs
def page_logs_admin():
    st.title(t("menu_logs"))
    df = logs.recent_actions(1000)
    st.dataframe(df)

# Router
def route(main_sel, sub_sel):
    if main_sel == t("menu_dashboard"):
        page_dashboard()
    elif main_sel == t("menu_customers"):
        if sub_sel == t("menu_customers_add"):
            page_customers_add()
        else:
            page_customers_list()
    elif main_sel == t("menu_followups"):
        if sub_sel == t("menu_followups_today"):
            page_followups_today()
        else:
            page_followups_all()
    elif main_sel == t("menu_backup"):
        # admin only for backup button? But everyone can see info
        page_backup()
    elif main_sel == t("menu_settings"):
        # admin-only subpages
        if st.session_state.get("role") != "admin":
            st.warning("Admin only")
            return
        if sub_sel == t("menu_users"):
            page_users_admin()
        elif sub_sel == t("menu_translations"):
            page_translations_admin()
        elif sub_sel == t("menu_logs"):
            page_logs_admin()
    else:
        st.info("Unknown page")

# ---------------------------
# Main entry
# ---------------------------
def main():
    # if not logged in -> show login area
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
                # set language from user record if present and valid
                user_lang = info.get("language")
                if user_lang in LANG_KEYS:
                    st.session_state["lang"] = user_lang
                st.rerun()
            else:
                st.error("用户名或密码错误")
        return

    # if logged in -> call route according to sidebar selection variables set earlier
    # We captured main_select and sub_select in sidebar context; because Streamlit runs top-down,
    # they are available as local variables; however to be safe, we reconstruct selection from UI:
    try:
        # Use the values from sidebar radio/selectbox (they are in local vars: main_select, sub_select)
        # Attempt to read from the top of this script's context
        ms = main_select
        ss = sub_select
    except Exception:
        # fallback to dashboard
        ms = t("menu_dashboard")
        ss = None

    route(ms, ss)

if __name__ == "__main__":
    main()
