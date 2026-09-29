import urllib.request
import json
import os

token = "B33WDA7uuuaGBx+97O7v2tJnGIJz2KA00g0kwzNu3Mg1rl5MisKFbLsMv5ydbrqaYiXFjV14WUiC5VZ5DjXUfN9SXCmHE58zMv/HrABVtE8DmVufJoLieEskFRr8gaFLBrTeI3QsDGhtM74Q5CrTagdB04t89/1O/w1cDnyilFU="
img_path = r"c:\Users\jason\Downloads\insurance-line-assistant\richmenu_2500x1686.png"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Define Rich Menu structure with ALL 4 Blocks bound to LIFF pages
rich_menu_data = {
    "size": {"width": 2500, "height": 1686},
    "selected": True,
    "name": "Insurance Assistant Main Menu All LIFF",
    "chatBarText": "點開選單",
    "areas": [
        {
            "bounds": {"x": 0, "y": 0, "width": 1250, "height": 843},
            "action": {
                "type": "uri",
                "label": "身分開通驗證",
                "uri": "https://liff.line.me/2011703143-uGCyFHl4"
            }
        },
        {
            "bounds": {"x": 1250, "y": 0, "width": 1250, "height": 843},
            "action": {
                "type": "uri",
                "label": "個人通知中心",
                "uri": "https://liff.line.me/2011703143-uGCyFHl4/notifications"
            }
        },
        {
            "bounds": {"x": 0, "y": 843, "width": 1250, "height": 843},
            "action": {
                "type": "uri",
                "label": "商品專區目錄",
                "uri": "https://liff.line.me/2011703143-uGCyFHl4/products"
            }
        },
        {
            "bounds": {"x": 1250, "y": 843, "width": 1250, "height": 843},
            "action": {
                "type": "uri",
                "label": "行政規範知識庫",
                "uri": "https://liff.line.me/2011703143-uGCyFHl4/guidelines"
            }
        }
    ]
}

print("1. Creating Rich Menu via LINE API...")
req = urllib.request.Request("https://api.line.me/v2/bot/richmenu", data=json.dumps(rich_menu_data).encode('utf-8'), headers=headers)
with urllib.request.urlopen(req) as resp:
    res_data = json.loads(resp.read().decode('utf-8'))
    rich_menu_id = res_data["richMenuId"]
    print(f"[OK] Rich Menu Created! ID: {rich_menu_id}")

# 2. Upload Image
print("2. Uploading high-res Rich Menu image...")
with open(img_path, 'rb') as f:
    img_bytes = f.read()

img_headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "image/png"
}
upload_url = f"https://api-data.line.me/v2/bot/richmenu/{rich_menu_id}/content"
req_img = urllib.request.Request(upload_url, data=img_bytes, headers=img_headers)
with urllib.request.urlopen(req_img) as resp:
    print(f"[OK] Image Uploaded successfully!")

# 3. Set Default Rich Menu
print("3. Setting as default Rich Menu for all users...")
set_url = f"https://api.line.me/v2/bot/user/all/richmenu/{rich_menu_id}"
req_set = urllib.request.Request(set_url, data=b"", headers=headers, method="POST")
with urllib.request.urlopen(req_set) as resp:
    print("[OK] Rich Menu set as DEFAULT for all LINE users!")

print("DONE! All 4 blocks (A, B, C, D) are now bound to dedicated LIFF pages!")
