from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

width = 2500
height = 1686

# Create main image
img = Image.new('RGBA', (width, height), (15, 23, 42, 255)) # Dark slate base
draw = ImageDraw.Draw(img)

# Load fonts
title_font = ImageFont.truetype('C:/Windows/Fonts/msjhbd.ttc', 96)
sub_font = ImageFont.truetype('C:/Windows/Fonts/msjh.ttc', 50)

def draw_gradient_card(box, color1, color2, radius=40):
    x1, y1, x2, y2 = box
    w = x2 - x1
    h = y2 - y1
    
    # Create card base
    card = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(card)
    
    # Fill gradient line by line inside mask
    for i in range(h):
        ratio = i / h
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        cdraw.line([(0, i), (w, i)], fill=(r, g, b, 255))
        
    # Create mask for rounded corners
    mask = Image.new('L', (w, h), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.rounded_rectangle([0, 0, w, h], radius=radius, fill=255)
    
    # Apply rounded mask
    card.putalpha(mask)
    img.paste(card, (x1, y1), card)
    
    # Draw subtle inner border
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, outline=(255, 255, 255, 60), width=4)

def draw_icon_badge(center_x, center_y, bg_color, icon_type):
    # Circle badge background
    r = 100
    draw.ellipse([center_x - r, center_y - r, center_x + r, center_y + r], fill=bg_color, outline=(255, 255, 255, 180), width=6)
    
    # Draw vector icon inside
    cx, cy = center_x, center_y
    if icon_type == "shield_key":
        # Draw Shield
        shield_pts = [(cx, cy - 50), (cx + 45, cy - 35), (cx + 35, cy + 25), (cx, cy + 55), (cx - 35, cy + 25), (cx - 45, cy - 35)]
        draw.polygon(shield_pts, fill=(255, 255, 255, 255))
        # Inner Keyhole
        draw.ellipse([cx - 12, cy - 20, cx + 12, cy + 4], fill=bg_color)
        draw.polygon([(cx - 8, cy - 4), (cx + 8, cy - 4), (cx + 12, cy + 25), (cx - 12, cy + 25)], fill=bg_color)

    elif icon_type == "bell":
        # Draw Bell
        draw.ellipse([cx - 35, cy - 35, cx + 35, cy + 15], fill=(255, 255, 255, 255))
        draw.rounded_rectangle([cx - 48, cy + 5, cx + 48, cy + 22], radius=8, fill=(255, 255, 255, 255))
        draw.ellipse([cx - 15, cy + 22, cx + 15, cy + 38], fill=(255, 255, 255, 255))
        draw.ellipse([cx - 8, cy - 48, cx + 8, cy - 32], fill=(255, 255, 255, 255))

    elif icon_type == "document":
        # Draw Document Folder / File
        draw.rounded_rectangle([cx - 40, cy - 45, cx + 40, cy + 45], radius=10, fill=(255, 255, 255, 255))
        draw.rectangle([cx - 25, cy - 25, cx + 25, cy - 17], fill=bg_color)
        draw.rectangle([cx - 25, cy - 5, cx + 25, cy + 3], fill=bg_color)
        draw.rectangle([cx - 25, cy + 15, cx + 10, cy + 23], fill=bg_color)

    elif icon_type == "book":
        # Draw Book
        draw.rounded_rectangle([cx - 45, cy - 40, cx + 45, cy + 40], radius=8, fill=(255, 255, 255, 255))
        draw.line([(cx, cy - 40), (cx, cy + 40)], fill=bg_color, width=8)
        draw.line([(cx - 30, cy - 15), (cx - 10, cy - 15)], fill=bg_color, width=6)
        draw.line([(cx + 10, cy - 15), (cx + 30, cy - 15)], fill=bg_color, width=6)
        draw.line([(cx - 30, cy + 10), (cx - 10, cy + 10)], fill=bg_color, width=6)
        draw.line([(cx + 10, cy + 10), (cx + 30, cy + 10)], fill=bg_color, width=6)

# Grid Card Definitions
cards_data = [
    {
        "box": (40, 40, 1230, 823),
        "c1": (16, 185, 129), # #10B981 Emerald
        "c2": (4, 120, 87),    # #047857 Dark Emerald
        "icon": "shield_key",
        "badge_bg": (6, 95, 70, 255),
        "title": "身分開通驗證",
        "desc": "輸入工號與 OTP 進行身分綁定"
    },
    {
        "box": (1270, 40, 2460, 823),
        "c1": (245, 158, 11),  # #F59E0B Amber
        "c2": (180, 83, 9),    # #B45309 Dark Amber
        "icon": "bell",
        "badge_bg": (146, 64, 14, 255),
        "title": "個人通知中心",
        "desc": "查看照會提醒與即時推播訊息"
    },
    {
        "box": (40, 863, 1230, 1646),
        "c1": (59, 130, 246),  # #3B82F6 Royal Blue
        "c2": (29, 78, 216),   # #1D4ED8 Dark Blue
        "icon": "document",
        "badge_bg": (30, 58, 138, 255),
        "title": "商品專區目錄",
        "desc": "瀏覽各類保險商品與銷售手冊"
    },
    {
        "box": (1270, 863, 2460, 1646),
        "c1": (139, 92, 246),  # #8B5CF6 Purple
        "c2": (109, 40, 217),  # #6D28D9 Dark Purple
        "icon": "book",
        "badge_bg": (91, 33, 182, 255),
        "title": "行政規範知識庫",
        "desc": "查詢業務規範與最新行政照會"
    }
]

for card in cards_data:
    x1, y1, x2, y2 = card["box"]
    draw_gradient_card(card["box"], card["c1"], card["c2"], radius=44)
    
    # Calculate text positions for perfect vertical balance
    badge_cx = x1 + 180
    badge_cy = y1 + (y2 - y1) // 2
    draw_icon_badge(badge_cx, badge_cy, card["badge_bg"], card["icon"])
    
    # Text offset
    text_x = x1 + 330
    title_y = y1 + 220
    desc_y = y1 + 440
    
    # Title with subtle shadow for 3D depth
    draw.text((text_x + 3, title_y + 3), card["title"], font=title_font, fill=(0, 0, 0, 120))
    draw.text((text_x, title_y), card["title"], font=title_font, fill=(255, 255, 255, 255))
    
    # Description Subtext
    draw.text((text_x + 2, desc_y + 2), card["desc"], font=sub_font, fill=(0, 0, 0, 100))
    draw.text((text_x, desc_y), card["desc"], font=sub_font, fill=(241, 245, 249, 230))

# Convert to RGB and save high quality PNG
final_img = img.convert('RGB')
out_path = r"c:\Users\jason\Downloads\insurance-line-assistant\richmenu_2500x1686.png"
final_img.save(out_path, quality=100)
print(f"Fancy Rich Menu image generated successfully at {out_path}")
