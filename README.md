# 超声医学问卷调查系统

基于 Flask 的超声影像诊断问卷调查系统，用于收集医生对超声影像的诊断评估数据，分析 AI 辅助诊断对医生判断的影响。

## 功能

- **用户注册/登录** — 收集医生的机构、科室、职称、从业经验等信息
- **影像诊断问卷** — 医生对超声影像进行特征标注（回声强度、形状规则、纵横比例、边界特征）并给出诊断结论
- **AI 辅助对照** — 同一案例随机分配 有/无 AI 推理辅助两种条件，形成对照实验
- **信心评级** — 医生对每次判断提交信心等级（低/中/高）
- **计时统计** — 自动记录每个案例的诊断耗时

## 项目结构

```
├── main.py                  # Flask 应用入口，路由定义
├── config.yaml              # 端口、日志等配置
├── .env                     # MongoDB 连接地址
├── migrate_to_mongo.py      # JSON → MongoDB 一次性迁移脚本
├── mongo_to_json.py         # MongoDB → JSON 导出脚本
├── requirements.txt         # Python 依赖
├── services/
│   ├── login_service.py     # 密码哈希与验证
│   └── record_service.py    # 问卷记录 CRUD（MongoDB）
├── utils/
│   ├── log.py               # 日志模块（按日期滚动）
│   ├── mongo.py             # MongoDB 操作封装
│   └── tools.py             # 通用工具函数
├── db/
│   ├── ai_reasoning.json    # 医学案例数据（影像路径、特征选项、标准答案）
│   └── images/              # 超声影像图片
├── templates/               # Jinja2 HTML 模板
│   ├── login.html           # 登录/注册页
│   ├── medwithai.html       # 问卷主页面
│   ├── instruction.html     # 操作说明页
│   ├── end.html             # 完成页
│   └── index.html           # 首页
└── assets/logo/             # 静态资源（Logo、背景图）
```

## 数据存储

| 数据 | 存储方式 | 说明 |
|------|---------|------|
| 用户信息 | MongoDB `users` 集合 | 用户名、密码哈希、机构、职称等 |
| 问卷记录 | MongoDB `records` 集合 | 案例列表、选项、耗时、信心等 |
| 医学案例 | `db/ai_reasoning.json` | 案例影像、特征选项、AI 推理、标准答案 |

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 MongoDB

编辑 `.env` 文件，设置 MongoDB 连接地址：

```
MONGO_URI=mongodb://localhost:27017
```

### 3. 迁移已有数据（可选）

如果之前使用 JSON 文件存储，运行迁移脚本将数据导入 MongoDB：

```bash
python migrate_to_mongo.py
```

反向导出（MongoDB → JSON）：

```bash
python mongo_to_json.py
```

### 4. 启动应用

```bash
python main.py
```

应用默认运行在 `http://0.0.0.0:13579`，端口可在 `config.yaml` 中修改。

## 配置说明

**config.yaml**

| 字段 | 默认值 | 说明 |
|------|--------|------|
| `port` | 13579 | 服务监听端口 |
| `log_file` | logs/{port}/Qustionaire | 日志输出目录 |

**.env**

| 变量 | 说明 |
|------|------|
| `MONGO_URI` | MongoDB 连接字符串 |

## API 接口

| 路由 | 方法 | 说明 |
|------|------|------|
| `/` | GET/POST | 登录/注册页 |
| `/login` | POST | 用户登录 |
| `/register` | POST | 用户注册 |
| `/interact` | GET | 问卷主页面 |
| `/checks` | POST | 获取指定页面的案例数据 |
| `/records` | POST | 提交诊断选择 |
| `/time` | POST | 提交诊断耗时 |
| `/finished` | GET | 完成页 |
| `/images/<filename>` | GET | 获取超声影像 |
