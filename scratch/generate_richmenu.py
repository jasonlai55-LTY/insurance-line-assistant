from PIL import Image, ImageDraw, ImageFont
import os

width = 2500
height = 1686

img = Image.new('RGB', (width, height), color='#1E293B')
draw = ImageDraw.Draw(img)

# Load fonts
title_font = ImageFont.truetype('C:/Windows/Fonts/msjhbd.ttc', 72)
sub_font = ImageFont.truetype('C:/Windows/Fonts/msjh.ttc', 40)
badge_font = ImageFont.truetype('C:/Windows/Fonts/msjhbd.ttc', 36)

cards = [
    {
        "box": (40, 40, 1230, 823),
        "bg": "#059669",
        "border": "#10B981",
        "badge": "A",
        "badge_bg": "#047857",
        "icon": "🔐",
        "title": "身分開通驗證",
        "desc": "輸入工號與 OTP 進行身分綁定"
    },
    {
        "box": (1270, 40, 2460, 823),
        "bg": "#D97706",
        "border": "#F59E0B",
        "badge": "B",
        "badge_bg": "#B45309",
        "icon": "🔔",
        "title": "個人通知中心",
        "desc": "查看照會提醒與即時推播訊息"
    },
    {
        "box": (40, 863, 1230, 1646),
        "bg": "#2563EB",
        "border": "#60A5FA",
        "badge": "C",
        "badge_bg": "#1D4ED8",
        "icon": "📄",
        "title": "商品專區目錄",
        "desc": "瀏覽各類保險商品與銷售手冊"
    },
    {
        "box": (1270, 863, 2460, 1646),
        "bg": "#7C3AED",
        "border": "#A78BFA",
        "badge": "D",
        "badge_bg": "#6D28D9",
        "icon": "📚",
        "title": "行政規範知識庫",
        "desc": "查詢業務規範與最新行政照會"
    }
]

for card in cards:
    x1, y1, x2, y2 = card["box"]
    r = 30
    
    # Outer container rounded rectangle
    draw.rounded_rectangle([x1, y1, x2, y2], radius=r, fill=card["bg"], outline=card["border"], width=6)
    
    # Grid Label Badge (A, B, C, D)
    draw.rounded_rectangle([x1+40, y1+40, x1+110, y1+100], radius=15, fill=card["badge_bg"])
    draw.text((x1+60, y1+48), card["badge"], font=badge_font, fill="#FFFFFF")
    
    # Icon and Title
    main_text = f"{card['icon']}  {card['title']}"
    draw.text((x1+150, y1+160), main_text, font=title_font, fill="#FFFFFF")
    
    # Description
    draw.text((x1+150, y1+280), card["desc"], font=sub_font, fill="#E2E8F0")

# Divider line in middle
draw.line([(1250, 20), (1250, 1666)], fill="#334155", width=4)
draw.line([(20, 843), (2480, 843)], fill="#334155", width=4)

out_path = r"c:\Users\jason\Downloads\insurance-line-assistant\richmenu_2500x1686.png"
img.save(out_path, quality=95)
print(f"Rich Menu image generated at {out_path}")
