import urllib.request
import json

token = "B33WDA7uuuaGBx+97O7v2tJnGIJz2KA00g0kwzNu3Mg1rl5MisKFbLsMv5ydbrqaYiXFjV14WUiC5VZ5DjXUfN9SXCmHE58zMv/HrABVtE8DmVufJoLieEskFRr8gaFLBrTeI3QsDGhtM74Q5CrTagdB04t89/1O/w1cDnyilFU="

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 1. Unlink any user specific rich menus if set
print("1. Unlinking default and user rich menus...")
try:
    req_del_def = urllib.request.Request("https://api.line.me/v2/bot/user/all/richmenu", headers=headers, method="DELETE")
    with urllib.request.urlopen(req_del_def) as resp:
        print("[OK] Cleared default rich menu link")
except Exception as e:
    print("No default link to clear:", e)

# 2. Get list of all rich menus
req_list = urllib.request.Request("https://api.line.me/v2/bot/richmenu/list", headers=headers)
with urllib.request.urlopen(req_list) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    menus = data.get("richmenus", [])
    print(f"Found {len(menus)} existing rich menu(s).")
    for m in menus:
        m_id = m["richMenuId"]
        name = m.get("name")
        print(f" - Deleting old menu: {m_id} ({name})")
        try:
            req_del = urllib.request.Request(f"https://api.line.me/v2/bot/richmenu/{m_id}", headers=headers, method="DELETE")
            with urllib.request.urlopen(req_del) as resp_del:
                print(f"   [OK] Deleted {m_id}")
        except Exception as ex:
            print(f"   Error deleting {m_id}:", ex)

print("Cleaned up all old rich menus!")
