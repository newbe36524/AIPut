"""
修复版本的远程服务器 - 解决 Wayland 环境导入问题
"""

# 在导入任何模块之前设置环境变量
import os
import sys

# 设置 DISPLAY 环境变量（如果需要）
if os.environ.get('WAYLAND_DISPLAY') and not os.environ.get('DISPLAY'):
    # 在 Wayland 环境下尝试使用 Xwayland
    os.environ['DISPLAY'] = ':0'

# 修复 sudo 环境下的 X11 授权问题
# 如果在 sudo 环境下运行，需要保留原用户的 XAUTHORITY
if os.geteuid() == 0:  # 检测是否为 root 用户
    # 尝试获取原始用户
    sudo_user = os.environ.get('SUDO_USER')
    if sudo_user and not os.environ.get('XAUTHORITY'):
        # 设置 XAUTHORITY 指向原用户的授权文件
        xauth_path = f'/home/{sudo_user}/.Xauthority'
        if os.path.exists(xauth_path):
            os.environ['XAUTHORITY'] = xauth_path

# 修复 pyautogui 的导入问题
# 在 Wayland 环境下不强制设置 DISPLAY，让适配器自行处理

# 加载配置文件（在导入其他模块之前）
try:
    from config import load_env
    load_env()
except ImportError:
    pass

# 现在可以安全地导入其他模块
import socket
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from flask import Flask, request, send_from_directory
import time
import logging
import qrcode
from PIL import Image, ImageTk
import asyncio
from typing import Optional

# 延迟导入平台相关模块
def init_platform_adapters():
    """延迟初始化平台适配器"""
    try:
        # 将 src 目录添加到模块搜索路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
        
        # 导入平台检测和适配器
        print("正在导入平台检测模块...")
        from platform_detection.detector import PlatformDetector

        print("正在导入适配器工厂...")
        from platform_adapters.factory import AdapterFactory

        # 检测平台
        print("正在检测平台...")
        platform_info = PlatformDetector.detect()
        print(f"\n=== 平台信息 ===")
        print(f"操作系统: {platform_info.os_name}")
        print(f"显示环境: {platform_info.display_protocol or '未知'}")
        print(f"桌面环境: {platform_info.desktop_environment or '未知'}")
        print(f"===============")

        # 检测到的工具
        if platform_info.additional_info:
            print("\n=== 可用工具 ===")
            kb_tools = platform_info.additional_info.get('keyboard_tools', [])
            cb_tools = platform_info.additional_info.get('clipboard_tools', [])
            if kb_tools:
                print(f"键盘模拟工具: {', '.join(kb_tools)}")
            if cb_tools:
                print(f"剪贴板工具: {', '.join(cb_tools)}")
            print("===============")

        # 创建适配器
        print("\n正在创建平台适配器...")
        adapters = AdapterFactory.create_adapters(platform_info)
        print("✓ 平台适配器创建成功！")

        return adapters, platform_info

    except ImportError as e:
        print(f"\n✗ 导入错误: {e}")
        print("⚠ 将使用兼容模式...")
        return None, None
    except Exception as e:
        print(f"\n✗ 平台适配器初始化失败: {e}")
        print("⚠ 将使用兼容模式...")
        return None, None

# Flask 应用配置
# 获取项目根目录
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
app = Flask(__name__, static_folder=os.path.join(project_root, 'site'), static_url_path='/static')
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# 全局变量
platform_adapters = None
platform_info = None
processing_service = None

# 在创建路由之前初始化平台适配器
print("正在初始化平台适配器...")
platform_adapters, platform_info = init_platform_adapters()

# 初始化AI处理服务
print("正在初始化AI处理服务...")
try:
    from ai.processing_service import ProcessingService
    processing_service = ProcessingService()
    print("  AI处理服务初始化成功")
except Exception as e:
    print(f"  AI处理服务初始化失败: {e}")
    processing_service = None

@app.route('/')
def index():
    # Get the directory containing this script (src directory)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to project root, then to site directory
    site_dir = os.path.join(script_dir, '..', 'site')
    return send_from_directory(site_dir, 'index.html')

@app.route('/type', methods=['POST'])
async def type_text():
    """处理文本输入请求，支持AI处理"""
    global platform_adapters, processing_service

    try:
        # 获取客户端IP地址
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))

        # 记录接收到的请求
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n[{timestamp}] 收到来自 {client_ip} 的请求")

        data = request.get_json()
        text = data.get('text', '')
        auto_submit = data.get('auto_submit', False)  # 获取自动提交参数

        # AI处理相关参数
        prompt = data.get('prompt', '')
        mode = data.get('mode', '')
        provider = data.get('provider', 'zai')

        # 输出要发送的文本（只显示前50个字符）
        display_text = text[:50] + "..." if len(text) > 50 else text
        print(f"  要输入的文本: {display_text}")
        print(f"  文本长度: {len(text)} 字符")
        if auto_submit:
            print("  勇敢模式: 开启 (将自动发送 Ctrl+Enter)")
        if mode:
            print(f"  AI处理模式: {mode}")

        # AI处理逻辑
        processed_text = text
        if prompt and processing_service:
            print(f"  正在使用AI处理文本...")
            try:
                result = await processing_service.process(
                    text=text,
                    prompt=prompt,
                    provider=provider,
                    mode=mode
                )
                if result is not None:
                    processed_text = result
                    # 显示处理后的文本（只显示前50个字符）
                    display_processed = processed_text[:50] + "..." if len(processed_text) > 50 else processed_text
                    print(f"  ✓ AI处理成功: {display_processed}")
                else:
                    print("  ⚠ AI处理失败，使用原始文本")
            except Exception as e:
                print(f"  ✗ AI处理出错: {e}")
                print("  继续使用原始文本")

        if processed_text and platform_adapters:
            print("  正在执行剪贴板操作...")
            # 使用平台适配器复制到剪贴板
            success = await platform_adapters.clipboard.copy_text(processed_text)
            if not success:
                print("  ✗ 剪贴板操作失败")
                error_msg = '剪贴板操作失败'
                if prompt:
                    error_msg += ' (AI处理已完成)'
                return {'success': False, 'error': error_msg}

            print("  ✓ 剪贴板操作成功")
            print("  正在发送粘贴命令...")
            # 等待剪贴板操作完成
            await asyncio.sleep(0.1)

            # 使用平台适配器发送粘贴命令
            success = await platform_adapters.keyboard.send_paste_command()

            if success:
                print("  ✓ 键盘模拟成功")

                # 播放提示音（如果启用）
                try:
                    # 检查是否禁用了声音提示
                    from config import get_config
                    sound_enabled = get_config('SOUND_NOTIFICATIONS', 'true').lower() == 'true'

                    if sound_enabled:
                        print("  声音提示已启用，正在播放...")
                        if hasattr(platform_adapters, 'notifications') and platform_adapters.notifications:
                            success = platform_adapters.notifications.play_notification_sound()
                            if success:
                                print("  ✓ 提示音播放成功")
                            else:
                                print("  ⚠ 提示音播放失败")
                        else:
                            print("  ⚠ 通知适配器未初始化")
                    else:
                        print("  声音提示已禁用")
                except Exception as e:
                    print(f"  ✗ 播放提示音异常: {e}")

                # 如果开启勇敢模式，发送 Ctrl+Enter
                if auto_submit:
                    print("  正在发送 Ctrl+Enter...")
                    # 等待粘贴完成
                    await asyncio.sleep(0.1)
                    # 发送 Ctrl+Enter
                    ctrl_enter_success = await platform_adapters.keyboard.send_ctrl_enter()
                    if ctrl_enter_success:
                        print("  ✓ Ctrl+Enter 发送成功")
                    else:
                        print("  ⚠ Ctrl+Enter 发送失败，文本已粘贴")

                response = {'success': True}
                # 如果进行了AI处理，添加相关信息
                if prompt and processed_text != text:
                    response['ai_processed'] = True
                    response['original_length'] = len(text)
                    response['processed_length'] = len(processed_text)

                return response
            else:
                # 如果键盘模拟失败，返回警告
                print("  ⚠ 键盘模拟失败，需要手动粘贴")
                response = {'success': True, 'warning': '已复制到剪贴板，请手动粘贴'}
                if prompt:
                    response['warning'] += ' (AI处理已完成)'
                return response
        else:
            if not processed_text:
                print("  ⚠ 警告: 接收到空文本")
                return {'success': False, 'error': '接收到空文本'}
            else:
                print("  ✗ 错误: 平台适配器未初始化")
                return {'success': False, 'error': '平台适配器未初始化'}

    except Exception as e:
        print(f"  ✗ 处理请求时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False}

def get_host_ip():
    """获取主要的本机 IP 地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def get_all_ips():
    """获取所有可用的本机 IP 地址"""
    ips = []
    try:
        hostname = socket.gethostname()
        addrs = socket.getaddrinfo(hostname, None)
        for addr in addrs:
            ip = addr[4][0]
            if ':' not in ip and ip != '127.0.0.1':
                if ip not in ips:
                    ips.append(ip)
    except Exception:
        pass

    if not ips:
        ips.append('127.0.0.1')

    # 排序逻辑
    priority_192 = []
    priority_10 = []
    other_ips = []
    virtual_ips = []

    for ip in ips:
        if ip.startswith('192.168.'):
            priority_192.append(ip)
        elif ip.startswith('10.'):
            priority_10.append(ip)
        elif ip.startswith('172.'):
            parts = ip.split('.')
            if len(parts) >= 2:
                second = int(parts[1])
                if 16 <= second <= 31:
                    virtual_ips.append(ip)
                else:
                    other_ips.append(ip)
        elif ip.startswith('198.18.'):
            virtual_ips.append(ip)
        else:
            other_ips.append(ip)

    ips = priority_192 + priority_10 + other_ips + virtual_ips

    main_ip = get_host_ip()
    if main_ip in ips:
        ips.remove(main_ip)
        if main_ip.startswith('192.168.'):
            insert_pos = 0
        elif main_ip.startswith('10.'):
            insert_pos = len(priority_192)
        else:
            insert_pos = len(priority_192) + len(priority_10)
        ips.insert(insert_pos, main_ip)

    ips.insert(0, '0.0.0.0 (所有网卡)')
    return ips

def get_qr_ips():
    """获取用于二维码的 IP 地址（排除 0.0.0.0）"""
    all_ips = get_all_ips()
    # 移除 0.0.0.0 选项
    qr_ips = [ip for ip in all_ips if not ip.startswith('0.0.0.0')]
    return qr_ips

def generate_qr_code(ip, port):
    """生成二维码图片"""
    try:
        # 构建URL
        url = f"http://{ip}:{port}"

        # 创建二维码
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        # 生成图片
        img = qr.make_image(fill_color="black", back_color="white")

        # 调整大小（可选）
        img = img.resize((250, 250), Image.Resampling.LANCZOS)

        return img, url
    except Exception as e:
        print(f"生成二维码失败: {e}")
        return None, None

# GUI 主程序
class ServerApp:
    def __init__(self, root):
        self.root = root

        # 确保平台适配器已初始化（可能已经在 Flask 启动时初始化了）
        global platform_adapters, platform_info
        if platform_adapters is None:
            print("正在初始化平台适配器...")
            platform_adapters, platform_info = init_platform_adapters()

        # 设置窗口标题
        title = "AIPut (跨平台版)"
        self.root.title(title)
        self.root.geometry("380x945")  # 630 * 1.5 = 945
        self.root.resizable(False, False)

        # 绑定窗口关闭事件
        self.root.protocol('WM_DELETE_WINDOW', self.quit_app)

        # 居中屏幕
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 380) // 2
        y = (screen_height - 945) // 2
        self.root.geometry(f"380x945+{x}+{y}")

        self.all_ips = get_all_ips()
        self.ip_var = tk.StringVar(value=self.all_ips[0])
        self.port_var = tk.StringVar(value="37856")
        self.is_running = False
        self.auto_start_enabled = True  # 默认启用自动启动

        # QR code 相关变量
        self.qr_ips = get_qr_ips()
        self.qr_ip_var = tk.StringVar(value=self.qr_ips[0] if self.qr_ips else "127.0.0.1")
        self.qr_photo = None

        # 主容器
        main_frame = tk.Frame(root, padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')

        # 显示环境信息
        if platform_info:
            env_text = f"操作系统: {platform_info.os_name}"
            if platform_info.display_protocol:
                env_text += f" | 显示: {platform_info.display_protocol}"
            if platform_info.desktop_environment:
                env_text += f" | 桌面: {platform_info.desktop_environment}"

            env_label = tk.Label(main_frame, text=env_text, fg="#888", font=("Arial", 9))
            env_label.pack(anchor='w', pady=(0, 10))

        # 其余UI代码...（简化版本）
        tk.Label(main_frame, text="本机 IP:", font=("Arial", 10, "bold")).pack(anchor='w')
        self.ip_combo = ttk.Combobox(main_frame, textvariable=self.ip_var,
                                     values=self.all_ips, font=("Arial", 10), state='normal')
        self.ip_combo.pack(fill='x', pady=(0, 10))

        tk.Label(main_frame, text="端口:", font=("Arial", 10, "bold")).pack(anchor='w')
        self.port_entry = tk.Entry(main_frame, textvariable=self.port_var, font=("Arial", 10))
        self.port_entry.pack(fill='x', pady=(0, 15))

        # 二维码 IP 选择
        tk.Label(main_frame, text="二维码 IP:", font=("Arial", 10, "bold")).pack(anchor='w')
        self.qr_ip_combo = ttk.Combobox(main_frame, textvariable=self.qr_ip_var,
                                       values=self.qr_ips, font=("Arial", 10), state='normal')
        self.qr_ip_combo.pack(fill='x', pady=(0, 15))

        # 二维码显示区域
        self.qr_frame = tk.Frame(main_frame, relief="solid", borderwidth=1, bg="#f5f5f5")

        # URL 显示
        self.qr_url_label = tk.Label(self.qr_frame, text="", font=("Arial", 10), fg="#007AFF", bg="#f5f5f5")

        # 二维码图片显示
        self.qr_image_label = tk.Label(self.qr_frame, bg="#f5f5f5")

        # 启动按钮
        self.btn_start = tk.Button(main_frame, text="启动服务", command=self.toggle_server,
                                   bg="#007AFF", fg="white", font=("Arial", 12, "bold"),
                                   relief="flat", pady=8, cursor="hand2")
        self.btn_start.pack(fill='x')

        # 提示信息
        tip_text = "使用平台抽象架构 - 自动适配您的操作系统"
        tip_label = tk.Label(main_frame, text=tip_text, fg="#888", font=("Arial", 8))
        tip_label.pack(pady=(10, 0))

        # 绑定事件
        self.qr_ip_var.trace_add('write', self.on_qr_ip_change)
        self.port_var.trace_add('write', self.on_port_change)

        # 显示初始二维码
        self.root.after(200, self.update_qr_code)

        # 自动启动服务
        if self.auto_start_enabled:
            # 延迟执行以确保UI完全加载
            self.root.after(100, self.auto_start_service)

    def auto_start_service(self):
        """自动启动服务"""
        try:
            # 验证端口配置
            port_str = self.port_var.get()
            if not port_str.isdigit():
                messagebox.showerror("配置错误", "端口配置无效，请手动启动服务")
                return

            port = int(port_str)

            # 端口范围检查
            if port < 1024 or port > 65535:
                messagebox.showerror("配置错误", "端口必须在 1024-65535 范围内，请手动启动服务")
                return

            host_ip = self.ip_var.get()

            if host_ip.startswith('0.0.0.0'):
                listen_host = '0.0.0.0'
            else:
                listen_host = host_ip

            # 启动 Flask
            t = threading.Thread(target=lambda: app.run(host=listen_host, port=port, debug=False, use_reloader=False), daemon=True)
            t.start()

            self.is_running = True
            self.btn_start.config(text="停止服务", bg="#ff3b30")
            self.port_entry.config(state='disabled')
            self.ip_combo.config(state='disabled')

            # 自动启动时不显示弹窗，避免打扰用户
            print(f"✓ 服务已自动启动在 http://{listen_host}:{port}")

        except Exception as e:
            messagebox.showerror("自动启动失败", f"服务自动启动失败：{str(e)}\n请检查配置后手动启动")

    def toggle_server(self):
        """切换服务器状态"""
        if not self.is_running:
            port_str = self.port_var.get()
            if not port_str.isdigit():
                messagebox.showerror("错误", "端口必须是数字")
                return

            port = int(port_str)
            host_ip = self.ip_var.get()

            if host_ip.startswith('0.0.0.0'):
                listen_host = '0.0.0.0'
            else:
                listen_host = host_ip

            # 启动 Flask
            t = threading.Thread(target=lambda: app.run(host=listen_host, port=port, debug=False, use_reloader=False), daemon=True)
            t.start()

            self.is_running = True
            self.btn_start.config(text="停止服务", bg="#ff3b30")
            self.port_entry.config(state='disabled')
            self.ip_combo.config(state='disabled')

            messagebox.showinfo("服务已启动", f"服务已启动在 http://{listen_host}:{port}")
        else:
            self.quit_app()

    def update_qr_code(self):
        """更新二维码显示"""
        try:
            # 验证端口
            port = self.port_var.get()
            if not port.isdigit():
                return

            # 获取当前选中的 IP
            qr_ip = self.qr_ip_var.get()

            # 生成二维码
            img, url = generate_qr_code(qr_ip, int(port))
            if img is None:
                return

            # 转换图片为 tkinter 可用的格式
            self.qr_photo = ImageTk.PhotoImage(img)

            # 更新 URL
            self.qr_url_label.config(text=url)

            # 更新二维码图片
            self.qr_image_label.config(image=self.qr_photo)
            self.qr_image_label.image = self.qr_photo

            # 显示二维码区域
            self.qr_url_label.pack(pady=(10, 5))
            self.qr_image_label.pack(pady=(0, 10))
            self.qr_frame.pack(fill='x', pady=(0, 15))

        except Exception as e:
            print(f"更新二维码失败: {e}")

    def on_qr_ip_change(self, *_, **__):
        """当 QR IP 选择变化时更新二维码"""
        self.update_qr_code()

    def on_port_change(self, *_, **__):
        """当端口变化时更新二维码"""
        self.update_qr_code()

    def quit_app(self):
        """退出应用"""
        if platform_adapters and hasattr(platform_adapters, 'system_tray'):
            platform_adapters.system_tray.stop()
        self.root.quit()

def signal_handler(signum, frame):
    """处理信号"""
    print("\n收到退出信号，正在退出...")
    sys.exit(0)

if __name__ == '__main__':
    # 注册信号处理器
    import signal
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # 创建并运行 GUI
    root = tk.Tk()
    app_gui = ServerApp(root)
    root.mainloop()