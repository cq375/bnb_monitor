#!/bin/bash
# BNB监控脚本部署脚本

set -e

echo "=== BNB余额监控服务部署 ==="
echo ""

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "错误: 请使用root权限运行此脚本"
    echo "使用: sudo bash deploy.sh"
    exit 1
fi

# 1. 安装Python3和pip
echo "[1/6] 检查Python3环境..."
if ! command -v python3 &> /dev/null; then
    echo "安装Python3..."
    apt-get update
    apt-get install -y python3 python3-pip
else
    echo "✓ Python3已安装: $(python3 --version)"
fi

# 2. 创建工作目录
echo ""
echo "[2/6] 创建工作目录..."
WORK_DIR="/root/hashfind"
mkdir -p $WORK_DIR
echo "✓ 工作目录: $WORK_DIR"

# 3. 复制文件
echo ""
echo "[3/6] 复制脚本文件..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$SCRIPT_DIR/bnb_monitor.py" $WORK_DIR/
cp "$SCRIPT_DIR/requirements.txt" $WORK_DIR/
chmod +x $WORK_DIR/bnb_monitor.py
echo "✓ 文件已复制"

# 4. 安装Python依赖
echo ""
echo "[4/6] 安装Python依赖..."
cd $WORK_DIR
pip3 install -r requirements.txt
echo "✓ 依赖安装完成"

# 5. 安装systemd服务
echo ""
echo "[5/6] 配置systemd服务..."
cp "$SCRIPT_DIR/bnb-monitor.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable bnb-monitor.service
echo "✓ 服务已配置并设置为开机自启"

# 6. 启动服务
echo ""
echo "[6/6] 启动服务..."
systemctl start bnb-monitor.service
sleep 2
systemctl status bnb-monitor.service --no-pager
echo ""

echo "=== 部署完成 ==="
echo ""
echo "服务管理命令:"
echo "  查看状态: systemctl status bnb-monitor"
echo "  查看日志: tail -f /var/log/bnb-monitor.log"
echo "  停止服务: systemctl stop bnb-monitor"
echo "  启动服务: systemctl start bnb-monitor"
echo "  重启服务: systemctl restart bnb-monitor"
echo "  禁用自启: systemctl disable bnb-monitor"
echo ""
echo "监控配置:"
echo "  监控地址: 0x748d173c03e1a2caa5b7c7ee81c8aac05fd03938"
echo "  余额阈值: 0.01 BNB"
echo "  检查间隔: 5分钟"
echo ""
