#!/usr/bin/env python3
"""
AI处理功能测试工具
用于测试AI配置是否正确，并验证API连接
"""

import os
import sys
import asyncio
import argparse

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 加载配置
try:
    from config import load_env
    load_env()
    print("✓ 已加载 .env 配置文件")
except ImportError:
    print("⚠ 未找到 config.py，将使用系统环境变量")

# 导入AI处理模块
try:
    from ai.anthropic_processor import AnthropicProcessor
    from ai.zai_processor import ZAIProcessor
    from ai.processing_service import ProcessingService
    print("✓ 已导入 AI 处理器")
except ImportError as e:
    print(f"✗ 导入失败: {e}")
    print("请确保已安装所有依赖：pip install python-dotenv aiohttp")
    sys.exit(1)


async def test_ai_config():
    """测试AI配置"""
    print("\n=== AI 配置测试 ===")

    # 检查 Anthropic 配置
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    anthropic_url = os.getenv("ANTHROPIC_API_BASE_URL")
    anthropic_model = os.getenv("ANTHROPIC_MODEL")
    default_provider = os.getenv("AI_PROCESSOR_DEFAULT", "anthropic")
    timeout = os.getenv("AI_PROCESSING_TIMEOUT", "30")

    print(f"默认处理器: {default_provider}")
    print(f"\nAnthropic 配置:")
    print(f"  API Key: {'✓ 已配置' if anthropic_key else '✗ 未配置'}")
    print(f"  API Base URL: {anthropic_url or '未配置'}")
    print(f"  Model: {anthropic_model or '未配置'}")

    # 检查 ZAI 配置（向后兼容）
    zai_key = os.getenv("ZAI_API_KEY")
    zai_url = os.getenv("ZAI_API_BASE_URL")
    zai_model = os.getenv("ZAI_MODEL")

    if zai_key:
        print(f"\nZAI 配置:")
        print(f"  API Key: ✓ 已配置")
        print(f"  API Base URL: {zai_url or '未配置'}")
        print(f"  Model: {zai_model or '未配置'}")

    print(f"\nTimeout: {timeout}秒")

    # 检查是否有可用的配置
    if default_provider == "anthropic" and not anthropic_key:
        print("\n❌ 错误：请先配置 ANTHROPIC_API_KEY")
        return False
    elif default_provider == "zai" and not zai_key:
        print("\n❌ 错误：请先配置 ZAI_API_KEY")
        return False

    return True


async def test_ai_connection(provider=None):
    """测试AI连接"""
    print("\n=== AI 连接测试 ===")

    try:
        # 使用处理服务
        service = ProcessingService()

        # 确定要使用的处理器
        if provider is None:
            provider = os.getenv("AI_PROCESSOR_DEFAULT", "anthropic")

        print(f"使用处理器: {provider}")

        # 测试简单文本
        test_text = "这是一个测试"
        test_prompt = "请将以下文本翻译成英文："

        print(f"\n测试输入：{test_text}")
        print(f"使用提示词：{test_prompt}")
        print("\n正在调用API...")

        # 调用AI处理
        result = await service.process(
            text=test_text,
            prompt=test_prompt,
            provider=provider
        )

        if result:
            print(f"\n✅ AI 处理成功！")
            print(f"输出结果：{result}")
            return True
        else:
            print("\n❌ AI 处理失败，返回空结果")
            return False

    except Exception as e:
        print(f"\n❌ 测试失败：{str(e)}")
        return False


async def test_specific_prompt(prompt_id=None, provider=None):
    """测试特定的提示词"""
    print("\n=== 提示词测试 ===")

    # 加载提示词配置
    try:
        import json
        with open('site/config/prompts.json', 'r', encoding='utf-8') as f:
            prompts_config = json.load(f)

        if prompt_id:
            # 测试指定的提示词
            prompt_data = next((p for p in prompts_config['prompts'] if p['id'] == prompt_id), None)
            if not prompt_data:
                print(f"❌ 未找到提示词：{prompt_id}")
                return False

            print(f"\n测试提示词：{prompt_data['name']}")
            print(f"描述：{prompt_data['description']}")

            if not prompt_data['prompt']:
                print("⚠ 这是'无处理'模式，跳过测试")
                return True

            test_text = "帮我整理一下这个项目的开发计划，我们需要做一个远程输入工具"
            print(f"\n测试文本：{test_text}")

            # 使用处理服务
            service = ProcessingService()
            if provider is None:
                provider = os.getenv("AI_PROCESSOR_DEFAULT", "anthropic")

            result = await service.process(
                text=test_text,
                prompt=prompt_data['prompt'],
                provider=provider
            )

            if result:
                print(f"\n✅ 处理成功！")
                print(f"输出：{result}")
                return True
            else:
                print(f"\n❌ 处理失败")
                return False
        else:
            # 列出所有可用的提示词
            print("\n可用的提示词：")
            for p in prompts_config['prompts']:
                print(f"  - {p['id']}: {p['name']}")
                print(f"    {p['description']}")

    except FileNotFoundError:
        print("❌ 未找到 prompts.json 文件")
        return False
    except Exception as e:
        print(f"❌ 加载提示词失败：{e}")
        return False


async def main():
    parser = argparse.ArgumentParser(description='AI处理功能测试工具')
    parser.add_argument('--prompt', '-p', help='测试特定的提示词ID')
    parser.add_argument('--text', '-t', help='测试的文本内容')
    parser.add_argument('--provider', help='指定AI处理器 (anthropic 或 zai)')
    args = parser.parse_args()

    print("AIPut AI 处理功能测试工具")
    print("=" * 50)

    # 测试配置
    config_ok = await test_ai_config()
    if not config_ok:
        print("\n请配置好AI设置后再运行测试")
        sys.exit(1)

    # 确定使用的处理器
    provider = args.provider or os.getenv("AI_PROCESSOR_DEFAULT", "anthropic")

    # 测试连接
    connection_ok = await test_ai_connection(provider)
    if not connection_ok:
        print("\n连接测试失败，请检查配置")
        sys.exit(1)

    # 测试特定提示词
    if args.prompt:
        await test_specific_prompt(args.prompt, provider)
    elif args.text:
        # 如果提供了文本参数，进行简单测试
        print("\n=== 文本处理测试 ===")
        service = ProcessingService()
        print(f"测试文本：{args.text}")
        print("处理中...")
        result = await service.process(
            text=args.text,
            prompt="请优化这段文字：",
            provider=provider
        )
        if result:
            print(f"\n输出：{result}")
        else:
            print("\n处理失败")
    else:
        # 显示可用提示词列表
        await test_specific_prompt(provider=provider)

        # 交互式测试
        print("\n=== 交互式测试 ===")
        print("输入文本进行测试（输入 'quit' 退出）：")

        service = ProcessingService()

        while True:
            try:
                text = input("\n输入: ").strip()
                if text.lower() == 'quit':
                    break

                if text:
                    print("处理中...")
                    result = await service.process(
                        text=text,
                        prompt="请优化这段文字：",
                        provider=provider
                    )
                    if result:
                        print(f"\n输出: {result}")
                    else:
                        print("处理失败")

            except KeyboardInterrupt:
                break

    print("\n测试完成！")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n测试已取消")
    except Exception as e:
        print(f"\n运行出错：{e}")
        import traceback
        traceback.print_exc()