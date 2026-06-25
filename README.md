# QQ Avatar Monitor

定时监控指定 QQ 用户的头像变更，检测到变化时通过邮件发送通知（含新头像附件）。

## 工作原理

```
定时循环 → 拉取 QQ 头像 → 计算哈希 → 与本地缓存比对 → 不同则发邮件通知
```

- 通过 QQ 公开 CDN 获取头像，无需 API Key 或登录凭证
- 使用哈希检测头像是否变更
- 状态持久化到本地 JSON 文件，程序重启不丢失历史记录
- 头像变更时通过 SMTP 发送通知邮件，新头像以附件形式附带

## 快速开始

```bash
git clone <repo-url> && cd qq_avatar_monitor

# 1. 创建虚拟环境并安装依赖
python3 -m venv venv
venv/bin/pip install -r requirements.txt

# 2. 生成配置文件
cp config.yaml.example config.yaml
vim config.yaml  # 填写 QQ 号和邮箱信息

# 3. 启动监控
venv/bin/python main.py
```

首次运行会自动拉取当前头像并保存哈希，后续检测到哈希变化即发送邮件。

## 配置说明

```yaml
qq:
  qq_number: "123456789"           # 被监控的 QQ 号
  check_interval_seconds: 300      # 检查间隔（秒）

email:
  smtp_server: "smtp.qq.com"       # SMTP 服务器地址
  smtp_port: 465                   # 端口 587(TLS) / 465(SSL)
  username: "your@qq.com"          # 邮箱账号
  password: "your_auth_code"       # 授权码或应用专用密码
  from_email: "your@qq.com"        # 发件人地址
  to_email: "notify@example.com"   # 收件人地址
  use_tls: false                   # 是否启用 TLS

state_file: "avatar_state.json"    # 状态缓存文件路径
```

## 邮箱授权码获取

| 邮箱 | 操作 |
|------|------|
| **QQ 邮箱** | 设置 → 账户 → POP3/SMTP 服务 → 开启 → 生成授权码 |
| **Gmail** | 开启两步验证 → [应用专用密码](https://myaccount.google.com/apppasswords) |
| **163/126** | 设置 → POP3/SMTP/IMAP → 开启 → 新增授权码 |
| **Outlook** | 安全性 → 双重验证 → 应用密码 |

## 后台运行

```bash
# 启动（后台运行，日志写入文件）
nohup venv/bin/python main.py > monitor.log 2>&1 &

# 查看实时日志
tail -f monitor.log

# 停止
pkill -f "main.py"
```

## 自定义配置路径

```bash
venv/bin/python main.py /path/to/your/config.yaml
```

## 项目文件

```
qq_avatar_monitor/
├── main.py              # 程序入口，事件循环
├── qq_monitor.py        # 头像拉取、哈希计算、状态管理
├── email_sender.py      # 邮件发送（SMTP）
├── config.py            # 配置加载（YAML + dataclass）
├── config.yaml          # 配置文件
├── config.yaml.example  # 配置模板
├── avatar_state.json    # 状态缓存（自动生成）
├── requirements.txt     # Python 依赖
└── README.md
```

## 局限性

- 仅能获取**公开头像**，隐私设置严格的 QQ 用户无法获取
- 依赖 QQ 公开 CDN 地址（`q.qlogo.cn` / `q1.qlogo.cn` 等），地址可能变更
- 如需更可靠的方案，建议使用 go-cqhttp / Lagrange.Core 等机器人框架通过官方 API 获取
