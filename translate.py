# translate.py
# 多语言翻译管理模块

import json
import os

TRANSLATION_FILE = 'translations.json'

# 默认五语初始词条
DEFAULT_TRANSLATIONS = {
    "中文": {
        "language_label":"选择语言",
        "menu_navigation":"导航",
        "menu_dashboard":"📊 Dashboard",
        "menu_customers":"👥 客户管理",
        "menu_customers_all":"全部客户",
        "menu_customers_add":"新增客户",
        "menu_followups":"📝 跟进记录",
        "menu_followups_today":"今日跟进",
        "menu_followups_all":"全部跟进",
        "menu_backup":"💾 GitHub 备份",
        "menu_settings":"⚙ 管理设置",
        "menu_users":"用户管理",
        "menu_translations":"翻译管理",
        "menu_logs":"操作日志",
        "login_title":"登录系统",
        "username":"用户名",
        "password":"密码",
        "btn_login":"登录",
        "btn_logout":"退出登录",
        "no_data":"暂无数据",
        "add_customer":"添加客户",
        "submit":"提交",
        "all_customers":"所有客户",
        "search_owner":"按主要负责人搜索",
        "input_customer_id":"输入客户 ID",
        "edit_customer":"编辑客户",
        "delete_customer":"删除客户",
        "confirm_delete":"确认删除该客户",
        "followup_note":"跟进内容",
        "next_action":"下一步动作",
        "followup_added":"跟进记录已创建",
        "level_pie":"客户等级占比",
        "trend":"成交趋势",
        "no_deal":"暂无成交数据",
        "chart_error":"无法生成图表（数据问题）",
        "backup_info":"自动备份使用 Streamlit Secrets: GITHUB_TOKEN / GITHUB_REPO / GITHUB_USERNAME",
        "backup_success":"备份成功",
        "backup_failed":"备份失败：",
        "export_excel":"导出 Excel",
        "owner_export":"导出负责人负责的客户（Excel）",
        "customer_details":"客户详情",
        "created_at":"创建时间",
        "action_logs":"操作日志",
        "add_user":"添加用户",
        "reset_password":"重置密码",
        "delete_user":"删除用户",
        "user_added":"用户已创建",
        "password_reset":"密码已重置",
        "user_deleted":"用户已删除",
        "translations_saved":"翻译已保存",
        "edit_customer_label":"编辑客户信息",
        "no_permission":"权限不足"
    },
    "English": {
        "language_label":"Select language",
        "menu_navigation":"Navigation",
        "menu_dashboard":"📊 Dashboard",
        "menu_customers":"👥 Customers",
        "menu_customers_all":"All Customers",
        "menu_customers_add":"Add Customer",
        "menu_followups":"📝 Followups",
        "menu_followups_today":"Today",
        "menu_followups_all":"All Followups",
        "menu_backup":"💾 GitHub Backup",
        "menu_settings":"⚙ Admin Settings",
        "menu_users":"User Management",
        "menu_translations":"Translations",
        "menu_logs":"Action Logs",
        "login_title":"Login",
        "username":"Username",
        "password":"Password",
        "btn_login":"Login",
        "btn_logout":"Logout",
        "no_data":"No data",
        "add_customer":"Add Customer",
        "submit":"Submit",
        "all_customers":"All Customers",
        "search_owner":"Search by main owner",
        "input_customer_id":"Input customer ID",
        "edit_customer":"Edit customer",
        "delete_customer":"Delete customer",
        "confirm_delete":"Confirm delete this customer",
        "followup_note":"Followup note",
        "next_action":"Next action",
        "followup_added":"Followup added",
        "level_pie":"Level distribution",
        "trend":"Deal trend",
        "no_deal":"No deals",
        "chart_error":"Cannot generate chart (data issue)",
        "backup_info":"Backups use Streamlit Secrets: GITHUB_TOKEN / GITHUB_REPO / GITHUB_USERNAME",
        "backup_success":"Backup success",
        "backup_failed":"Backup failed: ",
        "export_excel":"Export Excel",
        "owner_export":"Export owner's customers (Excel)",
        "customer_details":"Customer details",
        "created_at":"Created at",
        "action_logs":"Action Logs",
        "add_user":"Add user",
        "reset_password":"Reset password",
        "delete_user":"Delete user",
        "user_added":"User added",
        "password_reset":"Password reset",
        "user_deleted":"User deleted",
        "translations_saved":"Translations saved",
        "edit_customer_label":"Edit customer info",
        "no_permission":"No permission"
    },
    "Indonesian": {},
    "Khmer": {},
    "Vietnamese": {}
}


def load_translations():
    """加载翻译文件"""
    if os.path.exists(TRANSLATION_FILE):
        with open(TRANSLATION_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # 如果没有文件，使用默认词条
        return DEFAULT_TRANSLATIONS


def save_translations(obj: dict):
    """保存翻译文件"""
    with open(TRANSLATION_FILE, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
