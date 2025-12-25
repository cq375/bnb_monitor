# BNB余额监控脚本使用说明

## 功能说明
- 监控指定BSC地址的BNB余额
- 当余额低于设定阈值时自动发送通知
- 使用多个公共RPC节点，自动切换保证稳定性
- 防止重复通知（1小时冷却时间）

---

## 目录
- [服务器一键部署（推荐）](#服务器一键部署推荐)
- [本地安装步骤](#本地安装步骤)
- [运行方式](#运行方式)
- [配置说明](#配置说明)
- [故障排查](#故障排查)

---

## 服务器一键部署（推荐）

### 适用系统
- ✅ **Ubuntu 24.04 LTS**（强烈推荐）
- ✅ Ubuntu 22.04 LTS
- ✅ Debian 12
- ⚠️ CentOS/AlmaLinux（需修改脚本）

### 快速部署步骤

#### 1. 上传文件到服务器
在本地执行：
```bash
cd /path/to/hashfind
scp bnb_monitor.py requirements.txt bnb-monitor.service deploy.sh root@服务器IP:/root/
```

#### 2. SSH登录服务器
```bash
ssh root@服务器IP
```

#### 3. 执行一键部署
```bash
# 添加执行权限
chmod +x /root/deploy.sh

# 运行部署脚本
bash /root/deploy.sh
```

#### 4. 验证部署
```bash
# 查看服务状态
systemctl status bnb-monitor

# 查看实时日志
tail -f /var/log/bnb-monitor.log
```

### 部署成功标志
如果看到以下输出，说明部署成功：
```
[2025-12-25 11:38:46] 开始监控BNB余额
监控地址: 0x748d173c03e1a2caa5b7c7ee81c8aac05fd03938
余额阈值: 0.01 BNB
检查间隔: 300 秒
--------------------------------------------------
[2025-12-25 11:38:46] 成功连接到RPC: https://bsc-dataseed1.binance.org
[2025-12-25 11:38:46] 当前余额: 0.010375 BNB
[2025-12-25 11:38:46] ✓ 余额正常
```

---

## 本地安装步骤

### 1. 安装Python依赖
```bash
pip3 install -r requirements.txt
```

### 2. 配置脚本
编辑 `bnb_monitor.py` 文件，修改以下参数：

```python
MONITOR_ADDRESS = "0x你的地址"  # 替换为要监控的BSC地址
THRESHOLD = 0.01  # 余额阈值（BNB）
CHECK_INTERVAL = 300  # 检查间隔（秒），默认5分钟
```

## 运行方式

### 方式1：直接运行（前台）
```bash
python3 bnb_monitor.py
```

### 方式2：后台运行（推荐）
```bash
# 使用nohup后台运行
nohup python3 bnb_monitor.py > monitor.log 2>&1 &

# 查看日志
tail -f monitor.log

# 查看进程
ps aux | grep bnb_monitor

# 停止监控
pkill -f bnb_monitor.py
```

### 方式3：使用screen（推荐）
```bash
# 创建screen会话
screen -S bnb_monitor

# 运行脚本
python3 bnb_monitor.py

# 按 Ctrl+A 然后按 D 退出screen（脚本继续运行）

# 重新连接到screen
screen -r bnb_monitor

# 停止脚本：在screen中按 Ctrl+C
```

### 方式4：使用systemd服务（最稳定）
创建服务文件 `/etc/systemd/system/bnb-monitor.service`：

```ini
[Unit]
Description=BNB Balance Monitor
After=network.target

[Service]
Type=simple
User=你的用户名
WorkingDirectory=/path/to/hashfind
ExecStart=/usr/bin/python3 /path/to/hashfind/bnb_monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable bnb-monitor
sudo systemctl start bnb-monitor

# 查看状态
sudo systemctl status bnb-monitor

# 查看日志
sudo journalctl -u bnb-monitor -f
```

## 配置说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| MONITOR_ADDRESS | 要监控的BSC地址 | 必须配置 |
| THRESHOLD | 余额阈值（BNB） | 0.01 |
| CHECK_INTERVAL | 检查间隔（秒） | 300（5分钟） |
| alert_cooldown | 通知冷却时间（秒） | 3600（1小时） |

## 通知格式
当余额低于阈值时，会发送以下格式的通知：
```
⚠️ BNB余额警告

地址: 0x...
当前余额: 0.008 BNB
阈值: 0.01 BNB
时间: 2025-12-25 18:47:20
```

## 故障排查

### 常见问题及解决方案

#### ❌ 问题1：pip3 command not found
**现象**：执行部署脚本时提示 `pip3: command not found`

**解决方案**：
```bash
# 更新包列表
apt-get update

# 安装 pip3
apt-get install -y python3-pip

# 验证安装
pip3 --version

# 重新运行部署脚本
bash /root/deploy.sh
```

---

#### ❌ 问题2：externally-managed-environment 错误（Ubuntu 24.04）
**现象**：
```
error: externally-managed-environment
× This environment is externally managed
```

**原因**：Ubuntu 24.04 引入了 PEP 668 保护机制，防止直接使用 pip 安装系统级包。

**解决方案1（快速方案）**：
```bash
# 手动安装依赖（使用 --break-system-packages）
pip3 install --break-system-packages web3 requests

# 修改 deploy.sh 脚本
sed -i 's/pip3 install -r requirements.txt/pip3 install --break-system-packages -r requirements.txt/' /root/deploy.sh

# 重新运行部署
bash /root/deploy.sh
```

**解决方案2（使用虚拟环境）**：
```bash
# 安装 python3-venv
apt-get install -y python3-venv

# 创建虚拟环境
python3 -m venv /root/hashfind/venv

# 激活虚拟环境
source /root/hashfind/venv/bin/activate

# 安装依赖
pip install web3 requests

# 修改 service 文件使用虚拟环境的 Python
sed -i 's|/usr/bin/python3|/root/hashfind/venv/bin/python3|' /etc/systemd/system/bnb-monitor.service
```

---

#### ❌ 问题3：日志文件为空或无输出
**现象**：
- `tail -f /var/log/bnb-monitor.log` 无输出
- 服务状态显示运行中，但日志文件大小为 0

**原因**：Python 默认使用缓冲输出，不会立即写入日志文件。

**解决方案**：
```bash
# 修改 service 文件，添加 -u 参数（unbuffered 模式）
sed -i 's|ExecStart=/usr/bin/python3 /root/hashfind/bnb_monitor.py|ExecStart=/usr/bin/python3 -u /root/hashfind/bnb_monitor.py|' /etc/systemd/system/bnb-monitor.service

# 重新加载配置
systemctl daemon-reload

# 重启服务
systemctl restart bnb-monitor

# 等待几秒后查看日志
sleep 5
tail -f /var/log/bnb-monitor.log
```

---

#### ❌ 问题4：服务启动失败
**诊断步骤**：
```bash
# 1. 查看详细状态
systemctl status bnb-monitor -l

# 2. 查看系统日志
journalctl -u bnb-monitor -n 50 --no-pager

# 3. 手动测试脚本
cd /root/hashfind
python3 bnb_monitor.py

# 4. 检查 Python 路径
which python3

# 5. 检查文件权限
ls -la /root/hashfind/bnb_monitor.py
```

**常见原因**：
- Python 路径不正确
- 依赖包未安装
- 文件权限问题
- 地址格式错误

---

#### ❌ 问题5：无法连接RPC节点
**现象**：
```
[2025-12-25 11:38:46] 连接失败 https://bsc-dataseed1.binance.org: ...
```

**解决方案**：
```bash
# 1. 检查网络连接
ping -c 3 bsc-dataseed1.binance.org

# 2. 检查防火墙设置
ufw status

# 3. 测试 RPC 连接
curl -X POST https://bsc-dataseed1.binance.org \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'

# 4. 检查服务器是否限制出站连接
```

**说明**：脚本内置多个 RPC 节点，会自动切换。如果所有节点都失败，等待 60 秒后重试。

---

#### ❌ 问题6：通知发送失败
**现象**：
```
[2025-12-25 11:38:46] 通知发送失败: HTTP 400
```

**解决方案**：
```bash
# 1. 检查 webhook URL 是否正确
grep WEBHOOK_URL /root/hashfind/bnb_monitor.py

# 2. 测试 webhook 连接
curl -X POST https://hook.echobell.one/t/kb8ug8i75vcvf2mex3t9 \
  -H "Content-Type: application/json" \
  -d '{"text":"测试通知"}'

# 3. 检查网络是否能访问 echobell.one
ping -c 3 hook.echobell.one
```

---

#### ❌ 问题7：地址格式错误
**现象**：
```
错误: 无效的地址格式: 0x...
```

**解决方案**：
```bash
# 检查地址格式：
# ✅ 正确：0x748d173c03e1a2caa5b7c7ee81c8aac05fd03938（42个字符）
# ❌ 错误：748d173c03e1a2caa5b7c7ee81c8aac05fd03938（缺少0x）
# ❌ 错误：0x748d173c（长度不足）

# 修改监控地址
nano /root/hashfind/bnb_monitor.py
# 找到 MONITOR_ADDRESS 并修改为正确格式

# 重启服务
systemctl restart bnb-monitor
```

---

### 服务管理命令

```bash
# 查看服务状态
systemctl status bnb-monitor

# 启动服务
systemctl start bnb-monitor

# 停止服务
systemctl stop bnb-monitor

# 重启服务
systemctl restart bnb-monitor

# 查看实时日志
tail -f /var/log/bnb-monitor.log

# 查看系统日志
journalctl -u bnb-monitor -f

# 查看最近 50 条日志
journalctl -u bnb-monitor -n 50

# 查看是否开机自启
systemctl is-enabled bnb-monitor

# 启用开机自启
systemctl enable bnb-monitor

# 禁用开机自启
systemctl disable bnb-monitor
```

---

### 测试开机自启

```bash
# 1. 确认服务已启用
systemctl is-enabled bnb-monitor
# 输出应该是：enabled

# 2. 重启服务器
reboot

# 3. 重启后重新登录，检查服务状态
systemctl status bnb-monitor
# 应该显示：Active: active (running)

# 4. 查看日志确认正常运行
tail -20 /var/log/bnb-monitor.log
```

---

## 注意事项

### 运行环境
- ✅ 建议使用 **Ubuntu 24.04 LTS** 服务器
- ✅ 确保服务器有稳定的网络连接
- ✅ 建议使用 systemd 服务方式运行（自动重启、开机自启）

### 性能优化
- 公共 RPC 节点可能有请求限制，建议检查间隔不要太短（推荐 5 分钟）
- 如果需要更频繁的检查，建议使用付费 RPC 节点

### 安全建议
- 定期检查日志确保脚本正常运行
- 通知有 1 小时冷却时间，避免频繁发送
- 妥善保管 webhook URL，避免泄露

### 修改配置后的操作
```bash
# 修改配置文件
nano /root/hashfind/bnb_monitor.py

# 重启服务使配置生效
systemctl restart bnb-monitor

# 查看日志确认新配置生效
tail -f /var/log/bnb-monitor.log
```

---

## 部署经验总结

### ✅ 成功部署的关键点

1. **选择正确的操作系统**：Ubuntu 24.04 LTS 是最佳选择
2. **处理 PEP 668 限制**：Ubuntu 24.04 需要使用 `--break-system-packages` 或虚拟环境
3. **解决日志缓冲问题**：systemd 服务必须使用 `python3 -u` 参数
4. **验证部署**：部署后必须检查日志，确认 RPC 连接成功

### ⚠️ 容易出错的地方

1. 忘记添加 `-u` 参数导致日志无输出
2. Ubuntu 24.04 的 pip 保护机制阻止安装
3. 地址格式不正确（缺少 0x 或长度错误）
4. 防火墙阻止出站连接到 RPC 节点

### 📋 部署检查清单

- [ ] Python3 和 pip3 已安装
- [ ] 依赖包（web3、requests）已安装
- [ ] 监控地址格式正确（42个字符，以0x开头）
- [ ] systemd 服务配置正确
- [ ] 服务已启动并设置为开机自启
- [ ] 日志文件有输出
- [ ] RPC 连接成功
- [ ] 余额获取正常
