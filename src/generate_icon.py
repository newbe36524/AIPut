"""
生成应用程序图标
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    """创建一个简单的应用图标"""
    # 创建一个 256x256 的图像
    size = 256
    img = Image.new('RGB', (size, size), color='#007AFF')
    draw = ImageDraw.Draw(img)

    # 绘制圆角矩形背景
    margin = 20
    draw.rounded_rectangle(
        [(margin, margin), (size - margin, size - margin)],
        radius=30,
        fill='#007AFF'
    )

    # 绘制键盘图标（简化版）
    # 绘制三行键盘按键
    key_color = 'white'
    key_margin = 50
    key_height = 25
    key_spacing = 10

    # 第一行 - 5个键
    y1 = 60
    for i in range(5):
        x = key_margin + i * (30 + key_spacing)
        draw.rounded_rectangle(
            [(x, y1), (x + 30, y1 + key_height)],
            radius=5,
            fill=key_color
        )

    # 第二行 - 5个键
    y2 = y1 + key_height + key_spacing
    for i in range(5):
        x = key_margin + i * (30 + key_spacing)
        draw.rounded_rectangle(
            [(x, y2), (x + 30, y2 + key_height)],
            radius=5,
            fill=key_color
        )

    # 第三行 - 5个键
    y3 = y2 + key_height + key_spacing
    for i in range(5):
        x = key_margin + i * (30 + key_spacing)
        draw.rounded_rectangle(
            [(x, y3), (x + 30, y3 + key_height)],
            radius=5,
            fill=key_color
        )

    # 绘制手机图标（简化版）
    phone_x = size // 2 - 25
    phone_y = 150
    phone_width = 50
    phone_height = 80

    # 手机外框
    draw.rounded_rectangle(
        [(phone_x, phone_y), (phone_x + phone_width, phone_y + phone_height)],
        radius=8,
        fill='white',
        outline='white',
        width=2
    )

    # 手机屏幕
    screen_margin = 5
    draw.rounded_rectangle(
        [(phone_x + screen_margin, phone_y + screen_margin),
         (phone_x + phone_width - screen_margin, phone_y + phone_height - screen_margin - 10)],
        radius=5,
        fill='#E8F4FF'
    )

    # 绘制箭头（从手机指向上方）
    arrow_x = size // 2
    arrow_y1 = phone_y - 10
    arrow_y2 = y3 + key_height + 15

    # 箭头线
    draw.line([(arrow_x, arrow_y1), (arrow_x, arrow_y2)], fill='white', width=4)

    # 箭头头部
    arrow_size = 10
    draw.polygon([
        (arrow_x, arrow_y2),
        (arrow_x - arrow_size, arrow_y2 + arrow_size),
        (arrow_x + arrow_size, arrow_y2 + arrow_size)
    ], fill='white')

    # 保存为 PNG
    img.save('icon.png', 'PNG')
    print("图标已生成: icon.png")

    # 保存为 ICO（Windows 图标格式）
    # 创建多个尺寸的图标
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save('icon.ico', format='ICO', sizes=icon_sizes)
    print("Windows 图标已生成: icon.ico")

if __name__ == '__main__':
    create_icon()
