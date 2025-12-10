#!/bin/bash

# AIPut Fedora 系统依赖安装脚本
# 此脚本需要以 root 权限运行（使用 sudo）

echo "========================================="
echo "AIPut - 安装系统依赖"
echo "========================================="
echo

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    echo "此脚本需要 root 权限运行，请使用："
    echo "sudo $0"
    exit 1
fi

# 检查是否为 Fedora
if ! command -v dnf &> /dev/null; then
    echo "错误：此脚本仅适用于 Fedora 系统"
    exit 1
fi

echo "更新系统包..."
dnf update -y

echo
echo "安装开发工具..."
dnf groupinstall -y "Development Tools"

echo
echo "安装 Python 基础包..."
dnf install -y \
    python3 \
    python3-pip \
    python3-tkinter \
    python3-devel

echo
echo "安装 X11 和图形相关库..."
dnf install -y \
    libX11-devel \
    libXtst-devel \
    libXext-devel \
    libXinerama-devel \
    libXcursor-devel \
    libXi-devel

echo
echo "安装剪贴板和键盘模拟工具..."
dnf install -y \
    xclip \
    xdotool \
    xautomation \
    wl-clipboard \
    wtype \
    ydotool

echo
echo "安装编译依赖..."
dnf install -y \
    gcc \
    gcc-c++ \
    make \
    pkgconfig

echo
echo "安装可选依赖（提升性能）..."
dnf install -y \
    ImageMagick \
    scrot

echo
echo "========================================="
echo "系统依赖安装完成！"
echo "========================================="
echo
echo "接下来请运行："
echo "  ./install-fedora-user.sh"
echo "来安装 Python 依赖和配置用户环境"