#!/bin/bash

# AIPut 自动检测环境并启动

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查虚拟环境
if [ ! -d "aiput-env" ]; then
    echo "错误：虚拟环境不存在"
    echo "请先运行: ./install-fedora.sh"
    exit 1
fi

# 激活虚拟环境
source aiput-env/bin/activate

# 检测操作系统
OS_NAME=$(uname -s)
# 使用平台无关的版本
PYTHON_FILE="src/remote_server.py"
VERSION="跨平台通用版"

# 获取操作系统信息用于显示
case "$OS_NAME" in
    Linux*)
        OS="Linux"
        ;;
    Darwin*)
        OS="macOS"
        ;;
    CYGWIN*|MINGW*|MSYS*)
        OS="Windows"
        ;;
    *)
        echo "错误：不支持的操作系统 $OS_NAME"
        exit 1
        ;;
esac

# 检测显示环境和桌面环境（仅 Linux）
if [ "$OS" = "Linux" ]; then
    echo "检测运行环境..."
    if [ -n "$WAYLAND_DISPLAY" ]; then
        echo "- Wayland: 是"
    else
        echo "- Wayland: 否"
    fi

    if [ -n "$XDG_CURRENT_DESKTOP" ] && echo "$XDG_CURRENT_DESKTOP" | grep -qi kde; then
        echo "- KDE Plasma: 是"
    elif [ -n "$KDE_SESSION_VERSION" ]; then
        echo "- KDE Plasma: 是"
    else
        echo "- KDE Plasma: 否"
    fi
fi

# 检查Python文件是否存在
if [ ! -f "$PYTHON_FILE" ]; then
    echo "错误：找不到 $PYTHON_FILE"
    exit 1
fi

# 运行程序
echo "启动 AIPut ($VERSION)..."
echo "默认端口：37856"
echo

# 对于 Linux Wayland，给出必要的提示
if [ "$OS" = "Linux" ] && [ -n "$WAYLAND_DISPLAY" ]; then
    # 根据桌面环境给出不同的提示
    if [ -n "$XDG_CURRENT_DESKTOP" ] && echo "$XDG_CURRENT_DESKTOP" | grep -qi kde; then
        echo "提示：如果键盘模拟失败，请启用 plasma-virtual-keyboard"
        echo "系统设置 → 输入设备 → 虚拟键盘"
    else
        echo "提示：如果键盘模拟失败，请手动粘贴 (Ctrl+V)"
    fi
fi

# 运行主程序（它会自动检测并加载相应的平台适配器）
python3 $PYTHON_FILE