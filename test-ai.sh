#!/bin/bash

# AI功能测试脚本

# 检查参数
CI_MODE=false
if [ "$1" = "--ci" ]; then
    CI_MODE=true
    shift
fi

echo "AIPut AI 测试工具"
if [ "$CI_MODE" = true ]; then
    echo "=================="
    echo "(CI Mode - No Interaction)"
else
    echo "=================="
fi

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误：未找到 Python3"
    exit 1
fi

# 激活虚拟环境（如果存在）
if [ -d "aiput-env" ]; then
    echo "激活虚拟环境..."
    source aiput-env/bin/activate
elif [ -f "venv/bin/activate" ]; then
    echo "激活虚拟环境..."
    source venv/bin/activate
fi

# 检查依赖
echo "检查依赖..."
python3 -c "import aiohttp" 2>/dev/null || {
    echo "错误：缺少 aiohttp，正在安装..."
    pip install aiohttp python-dotenv
}

# 如果没有参数，运行自动测试
if [ $# -eq 0 ]; then
    echo ""
    echo "没有指定参数，运行自动测试..."
    echo ""

    # 测试 Anthropic（如果配置了）
    if [ -f ".env" ] && grep -q "ANTHROPIC_API_KEY=" .env && ! grep -q "ANTHROPIC_API_KEY=your_" .env; then
        echo "1. 测试 Anthropic Claude..."
        python3 test_ai.py --provider anthropic --text "Hello, how are you?"
        echo ""
    fi

    # 测试 ZAI（如果配置了）
    if [ -f ".env" ] && grep -q "ZAI_API_KEY=" .env && ! grep -q "ZAI_API_KEY=your_" .env; then
        echo "2. 测试 ZAI (智谱AI)..."
        python3 test_ai.py --provider zai --text "你好，这是一个测试"
        echo ""
    fi

    # 测试提示词功能
    if [ -f ".env" ] && (grep -q "ANTHROPIC_API_KEY=" .env && ! grep -q "ANTHROPIC_API_KEY=your_" .env || grep -q "ZAI_API_KEY=" .env && ! grep -q "ZAI_API_KEY=your_" .env); then
        echo "3. 测试任务整理提示词..."
        python3 test_ai.py --prompt agent-task --text "帮我整理一下这个项目的开发计划，我们需要做一个远程输入工具"
    else
        echo "未检测到有效的 API Key 配置"
        echo "请先配置 .env 文件"
        exit 1
    fi

    echo ""
    echo "自动测试完成！"

    if [ "$CI_MODE" = false ]; then
        echo ""
        echo "如需交互式测试，请运行: ./test-ai.sh --interactive"
    fi
else
    # 有参数，正常运行
    echo ""
    echo "运行 AI 测试..."
    echo ""

    # 在 CI 模式下，如果没有提供足够的参数，使用默认值
    if [ "$CI_MODE" = true ]; then
        # 如果只提供了 --provider 但没有 --text 或 --prompt，添加默认值
        has_provider=false
        has_text=false
        has_prompt=false

        for arg in "$@"; do
            case $arg in
                --provider)
                    has_provider=true
                    ;;
                --text)
                    has_text=true
                    ;;
                --prompt)
                    has_prompt=true
                    ;;
            esac
        done

        # 如果只有 provider 但没有 text 或 prompt，添加默认 text
        if [ "$has_provider" = true ] && [ "$has_text" = false ] && [ "$has_prompt" = false ]; then
            echo "(CI模式: 使用默认测试文本)"
            python3 test_ai.py "$@" --text "这是一个自动化测试"
        else
            python3 test_ai.py "$@"
        fi
    else
        python3 test_ai.py "$@"
    fi
fi