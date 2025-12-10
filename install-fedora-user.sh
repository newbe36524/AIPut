#!/bin/bash

# AIPut Fedora 用户环境安装脚本
# 此脚本以普通用户权限运行

echo "========================================="
echo "AIPut - 安装用户环境"
echo "========================================="
echo

# 检查是否为 root 用户
if [ "$EUID" -eq 0 ]; then
    echo "请不要使用 root 用户运行此脚本"
    exit 1
fi

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "1. 创建虚拟环境..."
python3 -m venv aiput-env

echo
echo "2. 激活虚拟环境并升级 pip..."
source aiput-env/bin/activate
pip install --upgrade pip

echo
echo "3. 安装 Python 依赖..."
pip install flask pyautogui pyperclip qrcode pillow pystray

echo
echo "4. 检查安装..."
python3 -c "
import flask, pyautogui, pyperclip, qrcode, PIL, pystray
print('✓ 所有 Python 依赖安装成功！')

import subprocess
tools = ['xclip', 'xdotool', 'xte']
missing = []
for tool in tools:
    if not subprocess.run(['which', tool], capture_output=True).returncode == 0:
        missing.append(tool)

if missing:
    print('⚠ 缺少工具:', ', '.join(missing))
    print('  请先运行: sudo ./install-fedora-deps.sh')
else:
    print('✓ 所有系统工具已安装')
"

echo
echo "========================================="
echo "安装完成！"
echo "========================================="
echo
echo "使用方法："
echo "1. 启动程序："
echo "   ./run-fedora.sh"
echo
echo "2. 或手动启动："
echo "   source aiput-env/bin/activate"
echo "   python3 src/remote_server_linux.py"
echo
echo "3. 创建桌面快捷方式："
echo "   ./create-desktop-entry.sh"
echo
echo "默认端口：37856"