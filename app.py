# app.py v6.0 — 完整 AYaocustomers
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
from io import BytesIO
import uuid
import os

from config import PAGE_TITLE, PAGE_ICON
from db import init_db
import auth
import customers
import translate
import backup
import logs

# -------------------- 初始化 --------------------
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")
init_db()

LANG_KEYS = ["中文", "English", "Indonesian", "Khmer", "Vietnamese"]

# 默认五语翻译
DEFAULT_MIN = {
    "中文": {"language_label":"选择语言","menu_navigation":"导航","menu_dashboard":"📊 Dashboard","menu_customers":"👥 客户管理","menu_customers_add":"新增客户","menu_followups":"📝 跟进记录","menu_backup":"💾 GitHub 备份","menu_settings":"⚙ 管理设置","menu_users":"用户管理","menu_translations":"翻译管理","menu_logs":"操作日志","login_title":"登录系统","username":"用户名","password":"密码","btn_login":"登录","btn_logout":"退出登录","no_data":"暂无数据","add_customer":"添加客户","submit":"提交","all_customers":"所有客户","search_owner":"按主要负责人搜索","input_customer_id":"输入客户 ID","edit_customer_label":"编辑客户信息","followup_note":"跟进内容","next_action":"下一步动作","followup_added":"跟进记录已创建","customer_details":"客户详情"},
    "English": {"language_label":"Select language","menu_navigation":"Navigation","menu_dashboard":"📊 Dashboard","menu_customers":"👥 Customers","menu_customers_add":"Add Customer","menu_followups":"📝 Followups","menu_backup":"💾 GitHub Backup","menu_settings":"⚙ Admin Settings","menu_users":"User Management","menu_translations":"Translations","menu_logs":"Action Logs","login_title":"Login","username":"Username","password":"Password","btn_login":"Login","btn_logout":"Logout","no_data":"No data","add_customer":"Add Customer","submit":"Submit","all_customers":"All Customers","search_owner":"Search by main owner","input_customer_id":"Input customer ID","edit_customer_label":"Edit customer info","followup_note":"Followup note","next_action":"Next action","followup_added":"Followup added","customer_details":"Customer details"},
    "Indonesian": {"language_label":"Pilih bahasa","menu_navigation":"Navigasi","menu_dashboard":"📊 Dashboard","menu_customers":"👥 Pelanggan","menu_customers_add":"Tambah Pelanggan","menu_followups":"📝 Tindak Lanjut","customer_details":"Detail Pelanggan","followup_note":"Catatan tindak lanjut","next_action":"Tindakan berikutnya","followup_added":"Tindak lanjut ditambahkan"},
    "Khmer": {"language_label":"ជ្រើសរើសភាសា","menu_navigation":"ផ្លូវដំណើរ","menu_dashboard":"📊 ទំព័រដឹកនាំ","menu_customers":"👥 អតិថិជន","menu_customers_add":"បន្ថែមអតិថិជន","menu_followups":"📝 តាមដាន","customer_details":"ព័ត៌មានអតិថិជន","followup_note":"កំណត់តាមដាន","next_action":"សកម្មភាពបន្ទាប់","followup_added":"កំណត់តាមដានបានបន្ថែម"},
    "Vietnamese": {"language_label":"Chọn ngôn ngữ","menu_navigation":"Điều hướng","menu_dashboard":"📊 Dashboard","menu_customers":"👥 Khách hàng","menu_customers_add":"Thêm khách hàng","menu_followups":"📝 Theo dõi","customer_details":"Chi tiết khách hàng","followup_note":"Ghi chú theo dõi","next_action":"Hành động tiếp theo","followup_added":"Theo dõi đã thêm"}
}

TRANSLATIONS = translate.load_translations() if hasattr(translate, 'load_translations') else {}

def get_translations_for(lang):
    return {**DEFAULT_MIN.get(lang, {}), **TRANSLATIONS.get(lang, {})}

def t(key):
    lang = st.session_state.get('lang','中文')
    return get_translations_for(lang).get(key,key)

if 'lang' not in st.session_state:
    st.session_state['lang'] = '中文'

# -------------------- 辅助 --------------------
def df_to_excel_bytes(df: pd.DataFrame) -> bytes:
    out = BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='sheet1')
    return out.getvalue()

# -------------------- Sidebar --------------------
with st.sidebar:
    st.markdown(f"## {t('menu_navigation')}")
    current_lang = st.session_state.get('lang','中文')
    lang_choice = st.selectbox(t('language_label'), LANG_KEYS, index=LANG_KEYS.index(current_lang))
    if lang_choice != st.session_state['lang']:
        st.session_state['lang'] = lang_choice
        st.experimental_rerun()

    st.markdown('---')
    menu_options = [t('menu_dashboard'), t('menu_customers'), t('menu_followups'), t('menu_backup'), t('menu_settings')]
    st.session_state['main_select'] = st.radio('', menu_options, index=0)

# -------------------- 页面功能 --------------------
def page_dashboard():
    st.title(t('menu_dashboard'))
    df = customers.list_customers_df()
    if df is None or df.empty:
        st.info(t('no_data'))
        return
    st.metric("Total Customers", len(df))
    st.subheader("Level Distribution")
    try:
        chart = alt.Chart(df).mark_arc().encode(theta=alt.Theta('id',aggregate='count'), color='level:N')
        st.altair_chart(chart,use_container_width=True)
    except: pass

def page_customers_list():
    st.title(t('menu_customers'))
    df = customers.list_customers_df()
    if df is None or df.empty:
        st.info(t('no_data'))
        return
    st.dataframe(df)

    cid = st.text_input(t('input_customer_id'))
    if cid:
        cust = customers.get_customer(cid)
        if cust:
            st.json(cust)
            st.subheader("Followups")
            fu = customers.list_followups_df(cid)
            st.dataframe(fu)
            with st.form(f'form_followup_{cid}'):
                note = st.text_area(t('followup_note'))
                action = st.text_input(t('next_action'))
                if st.form_submit_button(t('submit')):
                    fid = str(uuid.uuid4())
                    customers.add_followup(cid, fid, st.session_state.get('username','system'), note, action)
                    st.success(t('followup_added'))
                    st.experimental_rerun()
            st.subheader("Upload Photo")
            uploaded_file = st.file_uploader("Choose a photo", type=["png","jpg","jpeg"])
            if uploaded_file:
                customers.save_customer_photo(cid, uploaded_file)
                st.success("Photo uploaded!")

def page_customers_add():
    st.subheader(t('menu_customers_add'))
    all_users = auth.list_users()['username'].tolist()
    with st.form('form_add_customer'):
        rec = {}
        rec['name'] = st.text_input('Name')
        rec['whatsapp'] = st.text_input('Whatsapp')
        rec['line'] = st.text_input('Line')
        rec['telegram'] = st.text_input('Telegram')
        rec['country'] = st.text_input('Country')
        rec['city'] = st.text_input('City')
        rec['age'] = st.number_input('Age',0,120)
        rec['job'] = st.text_input('Job')
        rec['income'] = st.text_input('Income')
        rec['marital_status'] = st.selectbox('Marital Status',['Single','Married','Divorced','Widowed'])
        rec['deal_amount'] = st.number_input('Deal Amount',0.0)
        rec['level'] = st.selectbox('Level',['Normal','Important','VIP'])
        rec['progress'] = st.selectbox('Progress',['Pending','Negotiating','Completed','Lost'])
        rec['main_owner'] = st.selectbox('Main Owner', all_users)
        rec['assistant'] = st.selectbox('Assistant',['']+all_users)
        rec['notes'] = st.text_area('Notes')
        submitted = st.form_submit_button(t('submit'))
        if submitted:
            cid = str(uuid.uuid4())
            rec['id'] = cid
            rec['created_at'] = datetime.utcnow().isoformat()
            customers.insert_customer(rec)
            st.success(f"{t('add_customer')} {cid}")
            st.experimental_rerun()

# -------------------- Admin --------------------
def page_users_admin():
    if st.session_state.get('role') != 'admin':
        st.warning("No permission")
        return
    st.subheader(t('menu_users'))
    df = auth.list_users()
    st.dataframe(df)
    with st.form('add_user'):
        u = st.text_input('Username')
        p = st.text_input('Password')
        r = st.selectbox('Role',['user','admin'])
        lang_sel = st.selectbox('Default Language', LANG_KEYS)
        if st.form_submit_button(t('submit')):
            auth.add_user(u,p,r,lang_sel)
            st.success("User added")
            st.experimental_rerun()

def page_backup_admin():
    if st.session_state.get('role') != 'admin':
        st.warning("No permission")
        return
    st.subheader(t('menu_backup'))
    st.info("Backups use Streamlit Secrets for GitHub")
    if st.button('Run backup'):
        ok,msg = backup.backup_db_to_github(st.secrets, st.session_state.get('username','system'))
        if ok:
            st.success("Backup success")
        else:
            st.error(f"Backup failed: {msg}")

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
                st.session_state['role'] = info.get('role','user')
                lang = info.get('language')
                if lang in LANG_KEYS:
                    st.session_state['lang'] = lang
                st.experimental_rerun()
            else:
                st.error("Login failed")
        return

    main_page = st.session_state.get('main_select')
    if main_page == t('menu_dashboard'):
        page_dashboard()
    elif main_page == t('menu_customers'):
        page_customers_list()
        page_customers_add()
    elif main_page == t('menu_followups'):
        st.info("Followups integrated in customer details")
    elif main_page == t('menu_backup'):
        page_backup_admin()
    elif main_page == t('menu_settings'):
        page_users_admin()

if __name__ == '__main__':
    main()
