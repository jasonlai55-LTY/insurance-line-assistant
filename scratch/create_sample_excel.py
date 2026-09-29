import pandas as pd

data = [
    {
        "工號": "A001",
        "通訊處": "台北一處",
        "職級": "區經理",
        "通知類別": "行政照會",
        "通知標題": "【分眾發送】體檢報告補件提醒",
        "原始內文": "保戶張大明 (身分證 D123456789) 屬台北一處照會個案，請於本週五前完成補件。"
    },
    {
        "工號": "A001",
        "通訊處": "台北一處",
        "職級": "區經理",
        "通知類別": "營運活動",
        "通知標題": "【分眾發送】IQA 區經理大會報名通知",
        "原始內文": "台北一處區經理專屬：IQA 報名費 3000 元扣除通知與開會行程。"
    },
    {
        "工號": "A001",
        "通訊處": "台北一處",
        "職級": "區經理",
        "通知類別": "商品異動",
        "通知標題": "【分眾發送】ACC01 專屬銷售手冊",
        "原始內文": "台北一處專屬：ACC01 最新費率表已於系統發布，請下載查看。"
    }
]

df = pd.DataFrame(data)
out_path = r"c:\Users\jason\Downloads\insurance-line-assistant\分眾標籤照會示範檔_20260925.xlsx"
df.to_excel(out_path, index=False)
print(f"Tag Sample Excel generated successfully at {out_path}")
