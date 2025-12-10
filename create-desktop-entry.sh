#!/bin/bash

# 创建桌面入口文件脚本

echo "创建 AIPut 桌面快捷方式..."

# 获取当前目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/qaa-airtype-env"

# 检查虚拟环境是否存在
if [ ! -d "$VENV_DIR" ]; then
    echo "错误：虚拟环境不存在，请先运行 ./install-fedora.sh"
    exit 1
fi

# 创建 desktop 文件
cat > "$HOME/.local/share/applications/aiput.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=AIPut (Linux)
Comment=无线语音输入工具
Exec=$SCRIPT_DIR/run-fedora.sh
Icon=$SCRIPT_DIR/icon.png
Terminal=false
Categories=Utility;Application;
StartupNotify=true
EOF

# 创建运行脚本
cat > "$SCRIPT_DIR/run-fedora.sh" << EOF
#!/bin/bash
cd "$SCRIPT_DIR"
source "$VENV_DIR/bin/activate"
python3 src/remote_server_linux.py
EOF

chmod +x "$SCRIPT_DIR/run-fedora.sh"

# 如果图标不存在，创建一个简单的
if [ ! -f "$SCRIPT_DIR/icon.png" ]; then
    echo "创建默认图标..."
    # 使用 ImageMagick 创建简单图标（如果可用）
    if command -v convert &> /dev/null; then
        convert -size 64x64 xc:'#007AFF' "$SCRIPT_DIR/icon.png"
    else
        echo "提示：安装 ImageMagick 可以创建图标：sudo dnf install ImageMagick"
    fi
fi

echo "桌面快捷方式创建成功！"
echo "您可以在应用程序菜单中找到 AIPut"