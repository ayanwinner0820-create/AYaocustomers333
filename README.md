AYaocustomers

模块化 Streamlit 客户管理系统，包含：
- 登录/用户系统（管理员/普通用户）
- SQLite 存储（users, customers, followups, action_logs）
- 客户详情页、编辑、删除、跟进记录
- 多语言（中文/English/Indonesia/ខ្មែរ/Tiếng Việt）
- 按负责人报表（占比、成交趋势、成功率）
- 导出 Excel、按时间筛选
- GitHub 自动备份模块（可选，需在 Streamlit Secrets 设置 TOKEN)

部署：
1. 在你的仓库创建这些文件并 commit.
2. 在 Streamlit Cloud 新建应用，选择该仓库并运行.
3. 在 Secrets 中（如果需要自动备份）添加： GITHUB_TOKEN、GITHUB_REPO（格式：username/AYaocustomersremark）、GITHUB_USERNAME

默认管理员：用户名 `admin`，密码 `admin123`。首次登陆请修改密码.
