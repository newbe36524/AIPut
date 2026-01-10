# Project Context

## Purpose
AIPut 是一个通过手机端语音输入实现电脑端远程输入的 AI 增强工具。该项目允许用户使用手机浏览器访问本地 Web 界面，通过语音识别（推荐使用豆包输入法）将语音转换为文字，并可选地通过 AI（智谱AI）进行智能处理后，自动输入到电脑当前焦点的应用程序中。

核心功能包括：
- 无线远程输入：手机作为无线键盘，文字自动输入到电脑
- AI 智能处理：支持任务整理、口语书面化、即时翻译等提示词模式
- 勇敢模式：自动发送，实现真正的"说完即发送"
- 跨平台支持：Linux（X11/Wayland）、macOS、Windows
- 二维码快速连接：自动生成二维码供手机扫描访问

## Tech Stack
- **Python 3.8+** - 主要开发语言
- **Flask 3.0+** - Web 服务器框架，提供移动端界面
- **HTML5/CSS3/JavaScript** - 移动端 Web 界面
- **PyAutoGUI 0.9.54+** - 跨平台键盘/鼠标模拟
- **Pyperclip 1.8.2+** - 剪贴板操作
- **QRCode 7.4.2+** - 二维码生成
- **Pillow 10.0.0+** - 图像处理
- **PyStray 0.19.0+** - 系统托盘集成
- **AIOHTTP 3.8.0+** - 异步 HTTP 客户端
- **Python-dotenv 1.0.0+** - 环境变量管理
- **智谱AI (GLM-4.6)** - AI 处理服务（可选）

### 平台特定依赖
- **Linux X11**: xdotool, xte, xvkbd（键盘模拟）、xclip/xsel（剪贴板）
- **Linux Wayland**: wtype, ydotool（键盘模拟）、wl-clipboard（剪贴板）
- **macOS**: osascript, afplay（系统操作）
- **Windows**: winsound（系统通知音）

## Project Conventions

### Code Style
- **Python 遵循 PEP 8** 规范
- 使用类型提示（Type Hints）提高代码可读性
- 文件编码使用 UTF-8
- 缩进使用 4 个空格
- 函数和类使用描述性命名，避免缩写
- 文档字符串使用中文（项目主要面向中文用户）

### Architecture Patterns
- **平台抽象层 (Platform Abstraction)**: 使用工厂模式和适配器模式实现跨平台支持
  - `platform_detection/` - 自动检测操作系统和显示服务器（X11/Wayland）
  - `platform_adapters/` - 平台特定适配器（Linux、macOS、Windows）
  - `platform_adapters/base.py` - 基础适配器接口定义
- **AI 处理器抽象**:
  - `ai/processor.py` - AI 处理器基类
  - `ai/zai_processor.py` - 智谱AI处理器实现
  - `ai/anthropic_processor.py` - Anthropic AI处理器实现
- **配置管理**:
  - 使用 `.env` 文件管理环境变量
  - `python-dotenv` 自动加载配置
  - 优先使用环境变量，其次使用默认值

### 目录结构
```
src/
├── ai/                      # AI 处理模块
│   ├── processor.py         # AI 处理器基类
│   ├── zai_processor.py     # 智谱AI处理器
│   ├── anthropic_processor.py  # Anthropic处理器
│   └── processing_service.py  # 处理服务
├── platform_adapters/       # 平台适配器
│   ├── base.py             # 基础接口
│   ├── factory.py          # 适配器工厂
│   ├── linux/              # Linux 适配器
│   │   ├── adapter.py      # Linux 主适配器
│   │   ├── x11.py          # X11 实现
│   │   └── wayland.py      # Wayland 实现
│   ├── macos/              # macOS 适配器
│   │   └── adapter.py
│   └── windows/            # Windows 适配器
│       └── adapter.py
├── platform_detection/      # 平台检测
│   ├── detector.py         # 平台检测器
│   └── capabilities.py     # 能力检测
├── assets/                  # 静态资源
├── config.py               # 配置加载
├── remote_server.py        # 主服务器程序
└── generate_icon.py        # 图标生成工具
site/                       # 移动端 Web 界面
├── index.html              # 主页面
├── app.js                  # 前端逻辑
├── style.css               # 样式文件
└── config/                 # 提示词配置
```

### Testing Strategy
- 当前项目主要通过手动测试验证功能
- 使用 `test_ai.py` 进行 AI 处理功能测试
- 平台特定功能在各平台上进行手动验证

### Git Workflow
- **主分支**: `main`
- **功能分支**: 使用描述性名称，如 `feature/keep-alive-keyboard-activity`
- **提交信息规范**:
  - `feat:` - 新功能
  - `fix:` - Bug 修复
  - `docs:` - 文档更新
  - `refactor:` - 代码重构
  - `chore:` - 杂项（依赖更新等）
- **OpenSpec 工作流**:
  1. 创建变更提案：`openspec/changes/<change-id>/`
  2. 实现变更
  3. 归档变更：移动到 `openspec/changes/archive/YYYY-MM-DD-<change-id>/`

## Domain Context

### 核心概念
- **提示词 (Prompt)**: AI 处理的预定义模板，如"任务整理"、"口语书面化"、"翻译为英文"
- **勇敢模式 (Brave Mode)**: 自动发送模式，文本输入后自动按下 Ctrl+Enter 发送
- **保持活动 (Keep-Alive)**: 防止系统休眠的机制，通过模拟键盘活动实现
- **平台检测**: 自动识别操作系统和显示服务器（X11/Wayland）

### 用户交互流程
1. 用户在电脑上启动 `remote_server.py`
2. 程序生成二维码，用户用手机浏览器扫描
3. 用户在手机上选择提示词模式（可选）
4. 用户使用豆包输入法进行语音输入
5. 识别的文字发送到电脑服务器
6. 如选择了 AI 模式，服务器通过 AI 处理文本
7. 处理后的文字自动输入到电脑当前焦点程序

### 支持的 AI 提示词模式
- **无提示词**: 直接输入，不进行处理
- **任务整理**: 将散乱的口语化描述整理成条理清晰的任务列表
- **口语书面化**: 将口语化表达转换为规范的书面语言
- **翻译为英文**: 实时翻译，实现即时的口译效果

## Important Constraints
- **网络要求**: 手机和电脑必须在同一局域网内
- **系统要求**:
  - Linux: 需要 X11 或 Wayland 显示服务器
  - macOS: 需要 macOS 10.12+
  - Windows: 需要 Windows 10+
- **权限要求**:
  - Linux: 可能需要配置 Wayland 权限
  - 防火墙可能需要开放服务端口（默认 5000）
- **AI 服务限制**:
  - 需要智谱AI API Key（如使用 AI 处理功能）
  - API 调用有超时限制（默认 30 秒）
  - 网络连接到智谱AI服务必须稳定

## External Dependencies

### AI 服务
- **智谱AI (Zhipu AI / BigModel)**:
  - API Base URL: `https://open.bigmodel.cn/api/anthropic`
  - 模型: `glm-4.6`
  - 订阅优惠: https://www.bigmodel.cn/claude-code?ic=14BY54APZA

### 系统工具
- **Linux X11**: xdotool, xte, xvkbd, xclip
- **Linux Wayland**: wtype, ydotool, wl-copy, wl-paste
- **macOS**: osascript, afplay
- **Windows**: winsound

### 开发工具
- **OpenSpec CLI**: 规范驱动开发工具（`openspec` 命令）
- **Python 虚拟环境**: 推荐使用 `venv`（`aiput-env/`）

## OpenSpec 规范
项目使用 OpenSpec 进行规范驱动开发，关键规范包括：
- `specs/mobile-ui/spec.md` - 移动端界面规范
- `specs/ai-processing/spec.md` - AI 处理规范
- `specs/platform-abstraction/spec.md` - 平台抽象层规范
- `specs/notifications/spec.md` - 通知规范
- `specs/service-management/spec.md` - 服务管理规范

详见 `openspec/AGENTS.md` 了解如何使用 OpenSpec 工作流。
