#!/usr/bin/env python3
"""
BNB余额监控脚本
监控指定地址的BNB余额，当余额低于阈值时发送通知
"""

import time
import requests
from web3 import Web3
from datetime import datetime
import json

# 配置参数
MONITOR_ADDRESS = "0x地址"  # 替换为要监控的地址
THRESHOLD = 0.01  # BNB余额阈值
CHECK_INTERVAL = 300  # 检查间隔（秒），默认5分钟
WEBHOOK_URL = "你自己的webhook url" #下载 https://echobell.one/   填写邀请码4PSNG2QA获得100积分

# BSC公共RPC节点列表（备用）
RPC_URLS = [
    "https://bsc-dataseed1.binance.org",
    "https://bsc-dataseed2.binance.org",
    "https://bsc-dataseed3.binance.org",
    "https://bsc-dataseed4.binance.org",
    "https://bsc-dataseed1.defibit.io",
    "https://bsc-dataseed2.defibit.io",
]

# 全局变量
last_alert_time = 0
alert_cooldown = 3600  # 通知冷却时间（秒），避免频繁通知，默认1小时


def get_web3_connection():
    """尝试连接到BSC RPC节点"""
    for rpc_url in RPC_URLS:
        try:
            w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={'timeout': 10}))
            if w3.is_connected():
                print(f"[{datetime.now()}] 成功连接到RPC: {rpc_url}")
                return w3
        except Exception as e:
            print(f"[{datetime.now()}] 连接失败 {rpc_url}: {e}")
            continue
    return None


def get_bnb_balance(w3, address):
    """获取地址的BNB余额"""
    try:
        # 确保地址格式正确
        checksum_address = Web3.to_checksum_address(address)
        # 获取余额（单位：Wei）
        balance_wei = w3.eth.get_balance(checksum_address)
        # 转换为BNB
        balance_bnb = w3.from_wei(balance_wei, 'ether')
        return float(balance_bnb)
    except Exception as e:
        print(f"[{datetime.now()}] 获取余额失败: {e}")
        return None


def send_notification(address, balance):
    """发送通知到webhook"""
    global last_alert_time

    current_time = time.time()
    # 检查冷却时间
    if current_time - last_alert_time < alert_cooldown:
        print(f"[{datetime.now()}] 通知冷却中，跳过发送")
        return False

    try:
        message = f"⚠️ BNB余额警告\n\n地址: {address}\n当前余额: {balance:.6f} BNB\n阈值: {THRESHOLD} BNB\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        payload = {
            "text": message
        }

        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            print(f"[{datetime.now()}] 通知发送成功")
            last_alert_time = current_time
            return True
        else:
            print(f"[{datetime.now()}] 通知发送失败: HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"[{datetime.now()}] 发送通知异常: {e}")
        return False


def monitor_balance():
    """主监控循环"""
    print(f"[{datetime.now()}] 开始监控BNB余额")
    print(f"监控地址: {MONITOR_ADDRESS}")
    print(f"余额阈值: {THRESHOLD} BNB")
    print(f"检查间隔: {CHECK_INTERVAL} 秒")
    print("-" * 50)

    w3 = None

    while True:
        try:
            # 如果连接断开，重新连接
            if w3 is None or not w3.is_connected():
                w3 = get_web3_connection()
                if w3 is None:
                    print(f"[{datetime.now()}] 无法连接到任何RPC节点，等待重试...")
                    time.sleep(60)
                    continue

            # 获取余额
            balance = get_bnb_balance(w3, MONITOR_ADDRESS)

            if balance is not None:
                print(f"[{datetime.now()}] 当前余额: {balance:.6f} BNB")

                # 检查是否低于阈值
                if balance < THRESHOLD:
                    print(f"[{datetime.now()}] ⚠️  余额低于阈值！")
                    send_notification(MONITOR_ADDRESS, balance)
                else:
                    print(f"[{datetime.now()}] ✓ 余额正常")

            # 等待下次检查
            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            print(f"\n[{datetime.now()}] 监控已停止")
            break
        except Exception as e:
            print(f"[{datetime.now()}] 发生错误: {e}")
            time.sleep(60)  # 出错后等待1分钟再重试


if __name__ == "__main__":
    # 验证配置
    if MONITOR_ADDRESS == "0x你的地址":
        print("错误: 请先配置 MONITOR_ADDRESS")
        exit(1)

    if not Web3.is_address(MONITOR_ADDRESS):
        print(f"错误: 无效的地址格式: {MONITOR_ADDRESS}")
        exit(1)

    # 开始监控
    monitor_balance()