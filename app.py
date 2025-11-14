# app.py v1.1 — 完整 AYaocustomers 主入口
# 支持多语言、客户管理、跟进记录、Dashboard、GitHub备份、管理员功能

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

# -------------------- 初始化 --------------------
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")
init_db()

# -------------------- 翻译 --------------------
LANG_KEYS = ["中文", "English", "Indonesian", "Khmer", "Vietnamese"]
TRANSLATIONS = translate.load_translations() if hasattr(translate, 'load_translations') else {}

DEFAULT_MIN = {
    "中文": {"language_label":"选择语言", "menu_navigation":"导航", "menu_dashboard":"📊 Dashboard", "menu_customers":"👥 客户管理", "menu_customers_all":"全部客户", "menu_customers_add":"新增客户", "menu_followups":"📝 跟进记录", "menu_followups_today":"今日跟进", "menu_followups_all":"全部跟进", "menu_backup":"💾 GitHub 备份", "menu_settings":"⚙ 管理设置", "menu_users":"用户管理", "menu_translations":"翻译管理", "menu_logs":"操作日志", "login_title":"登录系统", "username":"用户名", "password":"密码", "btn_login":"登录", "btn_logout":"退出登录", "no_data":"暂无数据", "add_customer":"添加客户", "submit":"提交", "all_customers":"所有客户", "search_owner":"按主要负责人搜索", "input_customer_id":"输入客户 ID", "edit_customer":"编辑客户", "delete_customer":"删除客户", "confirm_delete":"确认删除该客户", "followup_note":"跟进内容", "next_action":"下一步动作", "followup_added":"跟进记录已创建", "level_pie":"客户等级占比", "trend":"成交趋势", "no_deal":"暂无成交数据", "chart_error":"无法生成图表（数据问题）", "backup_info":"自动备份使用 Streamlit Secrets: GITHUB_TOKEN / GITHUB_REPO / GITHUB_USERNAME", "backup_success":"备份成功", "backup_failed":"备份失败：", "export_excel":"导出 Excel", "owner_export":"导出负责人负责的客户（Excel）", "customer_details":"客户详情", "created_at":"创建时间", "action_logs":"操作日志", "add_user":"添加用户", "reset_password":"重置密码", "delete_user":"删除用户", "user_added":"用户已创建", "password_reset":"密码已重置", "user_deleted":"用户已删除", "translations_saved":"翻译已保存", "edit_customer_label":"编辑客户信息", "no_permission":"权限不足"}},
    "English": {"language_label":"Select language", "menu_navigation":"Navigation", "menu_dashboard":"📊 Dashboard", "menu_customers":"👥 Customers", "menu_customers_all":"All Customers", "menu_customers_add":"Add Customer", "menu_followups":"📝 Followups", "menu_followups_today":"Today", "menu_followups_all":"All Followups", "menu_backup":"💾 GitHub Backup", "menu_settings":"⚙ Admin Settings", "menu_users":"User Management", "menu_translations":"Translations", "menu_logs":"Action Logs", "login_title":"Login", "username":"Username", "password":"Password", "btn_login":"Login", "btn_logout":"Logout", "no_data":"No data", "add_customer":"Add Customer", "submit":"Submit", "all_customers":"All Customers", "search_owner":"Search by main owner", "input_customer_id":"Input customer ID", "edit_customer":"Edit customer", "delete_customer":"Delete customer", "confirm_delete":"Confirm delete this customer", "followup_note":"Followup note", "next_action":"Next action", "followup_added":"Followup added", "level_pie":"Level distribution", "trend":"Deal trend", "no_deal":"No deals", "chart_error":"Cannot generate chart (data issue)", "backup_info":"Backups use Streamlit Secrets: GITHUB_TOKEN / GITHUB_REPO / GITHUB_USERNAME", "backup_success":"Backup success", "backup_failed":"Backup failed: ", "export_excel":"Export Excel", "owner_export":"Export owner's customers (Excel)", "customer_details":"Customer details", "created_at":"Created at", "action_logs":"Action Logs", "add_user":"Add user", "reset_password":"Reset password", "delete_user":"Delete user", "user_added":"User added", "password_reset":"Password reset", "user_deleted":"User deleted", "translations_saved":"Translations saved", "edit_customer_label":"Edit customer info", "no_permission":"No permission"}}

if 'lang' not in st.session_state:
    st.session_state['lang'] = '中文'

def t(key: str) -> str:
    lang = st.session_state.get('lang', '中文')
    default = DEFAULT_MIN.get(lang, {})
    external = TRANSLATIONS.get(lang, {}) if isinstance(TRANSLATIONS, dict) else {}
    merged = default.copy()
    merged.update(external)
    return merged.get(key, key)

# -------------------- 辅助函数 --------------------
def df_to_excel_bytes(df: pd.DataFrame) -> bytes:
    from io import BytesIO
    out = BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='sheet1')
    return out.getvalue()

# -------------------- Sidebar --------------------
with st.sidebar:
    st.markdown(f"## {t('menu_navigation')}")
    lang_choice = st.selectbox(t('language_label'), LANG_KEYS, index=LANG_KEYS.index(st.session_state.get('lang','中文')))
    if lang_choice != st.session_state.get('lang'):
        st.session_state['lang'] = lang_choice
        st.rerun()

    st.markdown('---')
    main_options = [t('menu_dashboard'), t('menu_customers'), t('menu_followups'), t('menu_backup'), t('menu_settings')]
    st.session_state['main_select'] = st.radio('', main_options, index=0)

    if st.session_state['main_select'] == t('menu_customers'):
        st.session_state['sub_select'] = st.selectbox('', [t('menu_customers_all'), t('menu_customers_add')])
    elif st.session_state['main_select'] == t('menu_followups'):
        st.session_state['sub_select'] = st.selectbox('', [t('menu_followups_today'), t('menu_followups_all')])
    elif st.session_state['main_select'] == t('menu_settings'):
        st.session_state['sub_select'] = st.selectbox('', [t('menu_users'), t('menu_translations'), t('menu_logs')])
    else:
        st.session_state['sub_select'] = None

    st.markdown('---')
    if st.session_state.get('username'):
        st.markdown(f"**👤 {st.session_state.get('username')} ({st.session_state.get('role')})**")
        if st.button(t('btn_logout')):
            lang_keep = st.session_state.get('lang','中文')
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.session_state['lang'] = lang_keep
            st.rerun()

# -------------------- 页面函数 --------------------
def page_dashboard():
    st.title(t('menu_dashboard'))
    df = customers.list_customers_df()
    if df is None or df.empty:
        st.info(t('no_data'))
        return
    c1,c2,c3 = st.columns(3)
    c1.metric('Total', len(df))
    c2.metric('Owners', df['main_owner'].nunique() if 'main_owner' in df.columns else 0)
    c3.metric('Deals', df[df['progress']=='已成交'].shape[0] if 'progress' in df.columns else 0)

    st.subheader(t('level_pie'))
    try:
        pie = alt.Chart(df).mark_arc().encode(theta=alt.Theta(field='id', aggregate='count'), color='level:N')
        st.altair_chart(pie, use_container_width=True)
    except Exception:
        st.info(t('chart_error'))

    st.subheader('Country distribution / 国家分布')
    try:
        dfc = df.groupby('country').size().reset_index(name='count')
        bar = alt.Chart(dfc).mark_bar().encode(x='country:N', y='count:Q')
        st.altair_chart(bar, use_container_width=True)
    except Exception:
        st.info(t('chart_error'))

    st.subheader(t('trend'))
    try:
        df_deal = df[df['progress']=='已成交'].copy()
        if not df_deal.empty and 'created_at' in df_deal.columns:
            df_deal['date'] = pd.to_datetime(df_deal['created_at'], errors='coerce').dt.date
            trend = df_deal.groupby('date').size().reset_index(name='count')
            line = alt.Chart(trend).mark_line().encode(x='date:T', y='count:Q')
            st.altair_chart(line, use_container_width=True)
        else:
            st.info(t('no_deal'))
    except Exception:
        st.info(t('chart_error'))

# 页面路由
PAGE_MAP = {
    t('menu_dashboard'): page_dashboard,
    t('menu_customers_add'): lambda: page_customers_add(),
    t('menu_customers_all'): lambda: page_customers_list(),
    t('menu_followups_today'): lambda: page_followups_today(),
    t('menu_followups_all'): lambda: page_followups_all(),
    t('menu_backup'): lambda: page_backup_admin(),
    t('menu_users'): lambda: page_users_admin(),
    t('menu_translations'): lambda: page_translations_admin(),
    t('menu_logs'): lambda: page_logs_admin()
}

# -------------------- 主入口 --------------------
def main():
    if 'username' not in st.session_state:
        st.title(PAGE_TITLE)
        st.subheader(t('login_title'))
        username = st.text_input(t('username'))
        password = st.text_input(t('password'), type='password')
        if st.button(t('btn_login')):
            info = auth.authenticate(username.strip(), password.strip())
            if info:
                st.session_state['username'] = info['username']
                st.session_state['role'] = info.get('role', 'user')
                user_lang = info.get('language')
                if user_lang in LANG_KEYS:
                    st.session_state['lang'] = user_lang
                st.rerun()
            else:
                st.error('用户名或密码错误')
        return

    main_page = st.session_state.get('main_select', t('menu_dashboard'))
    sub_page = st.session_state.get('sub_select')
    func = PAGE_MAP.get(sub_page or main_page)
    if func:
        func()
    else:
        st.info('Page not found')

if __name__ == '__main__':
    main()
