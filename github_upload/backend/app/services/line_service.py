import httpx
from typing import List, Dict, Any
from app.core.config import settings


class LineMessagingService:
    """
    LINE Messaging API 推播與回覆服務
    """
    @staticmethod
    async def push_message(to_user_id: str, message_payload: Dict[str, Any]) -> bool:
        token = settings.LINE_CHANNEL_ACCESS_TOKEN
        if not token or token.startswith("mock_") or not to_user_id or to_user_id.startswith("U_MOCK"):
            return False
        
        url = "https://api.line.me/v2/bot/message/push"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        body = {
            "to": to_user_id,
            "messages": [message_payload]
        }
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(url, headers=headers, json=body, timeout=10.0)
                return res.status_code == 200
        except Exception as e:
            print("LINE Push Exception:", e)
            return False

    @staticmethod
    async def reply_message(reply_token: str, message_payload: Dict[str, Any]) -> bool:
        token = settings.LINE_CHANNEL_ACCESS_TOKEN
        if not token or token.startswith("mock_") or not reply_token:
            return False
        
        url = "https://api.line.me/v2/bot/message/reply"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        body = {
            "replyToken": reply_token,
            "messages": [message_payload]
        }
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(url, headers=headers, json=body, timeout=10.0)
                if res.status_code != 200:
                    print(f"❌ LINE Reply Error [{res.status_code}]: {res.text}")
                else:
                    print(f"✅ LINE Reply Success [200]")
                return res.status_code == 200
        except Exception as e:
            print("LINE Reply Exception:", e)
            return False


class LineFlexBuilder:
    """
    LINE Flex Message 卡片建造器
    - 回傳商品 DM / 銷售手冊 Flex Message 卡片
    - 回傳行政規範與保理賠指引卡片
    - 回傳歡迎與開通驗證卡片
    """

    @staticmethod
    def build_welcome_card() -> Dict[str, Any]:
        liff_id = settings.LINE_LIFF_ID
        return {
            "type": "flex",
            "altText": "【保險業務 LINE 助手】主選單與功能入口",
            "contents": {
                "type": "bubble",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": "#1DB446",
                    "contents": [
                        {
                            "type": "text",
                            "text": "🛡️ 保險業務 LINE 助手主選單",
                            "weight": "bold",
                            "color": "#FFFFFF",
                            "size": "md"
                        },
                        {
                            "type": "text",
                            "text": "請選擇您要開啟的服務功能：",
                            "weight": "bold",
                            "color": "#FFFFFF",
                            "size": "xs",
                            "wrap": True
                        }
                    ]
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "xs",
                    "contents": [
                        {
                            "type": "text",
                            "text": "歡迎使用！請完成身分開通以解鎖照會通知與完整保單個案詳情。",
                            "size": "xs",
                            "color": "#666666",
                            "wrap": True
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "style": "primary",
                            "color": "#1DB446",
                            "action": {
                                "type": "uri",
                                "label": "🔐 身分開通驗證",
                                "uri": f"https://liff.line.me/{liff_id}/login"
                            }
                        },
                        {
                            "type": "button",
                            "style": "secondary",
                            "action": {
                                "type": "uri",
                                "label": "🔔 個人通知中心",
                                "uri": f"https://liff.line.me/{liff_id}/notifications"
                            }
                        },
                        {
                            "type": "button",
                            "style": "secondary",
                            "action": {
                                "type": "uri",
                                "label": "📄 商品專區目錄",
                                "uri": f"https://liff.line.me/{liff_id}/products"
                            }
                        },
                        {
                            "type": "button",
                            "style": "secondary",
                            "action": {
                                "type": "uri",
                                "label": "📚 行政規範知識庫",
                                "uri": f"https://liff.line.me/{liff_id}/guidelines"
                            }
                        }
                    ]
                }
            }
        }

    @staticmethod
    def build_product_card(product_code: str, title: str, category_name: str, file_url: str, description: str = None) -> Dict[str, Any]:
        return {
            "type": "flex",
            "altText": f"【商品專區】{product_code} - {title}",
            "contents": {
                "type": "bubble",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": "#1DB446",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"【{category_name}】{product_code}",
                            "weight": "bold",
                            "color": "#FFFFFF",
                            "size": "sm"
                        },
                        {
                            "type": "text",
                            "text": title,
                            "weight": "bold",
                            "color": "#FFFFFF",
                            "size": "xl",
                            "wrap": True
                        }
                    ]
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": description or "點擊下方按鈕可在 LIFF 線上預覽與轉發給客戶。",
                            "size": "sm",
                            "color": "#666666",
                            "wrap": True
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "style": "primary",
                            "color": "#1DB446",
                            "action": {
                                "type": "uri",
                                "label": "線上預覽 / 一鍵轉發",
                                "uri": f"https://liff.line.me/{settings.LINE_LIFF_ID}/products?code={product_code}"
                            }
                        }
                    ]
                }
            }
        }

    @staticmethod
    def build_notification_card(category: str, title: str, masked_content: str) -> Dict[str, Any]:
        category_color = "#E53E3E" if category == "行政照會" else ("#3182CE" if category == "商品異動" else "#D69E2E")
        return {
            "type": "flex",
            "altText": f"【{category}】{title}",
            "contents": {
                "type": "bubble",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": category_color,
                    "contents": [
                        {
                            "type": "text",
                            "text": f"🔔 {category}",
                            "weight": "bold",
                            "color": "#FFFFFF",
                            "size": "sm"
                        },
                        {
                            "type": "text",
                            "text": title,
                            "weight": "bold",
                            "color": "#FFFFFF",
                            "size": "lg",
                            "wrap": True
                        }
                    ]
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": masked_content,
                            "size": "sm",
                            "color": "#333333",
                            "wrap": True
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "button",
                            "style": "secondary",
                            "action": {
                                "type": "uri",
                                "label": "開啟個人通知中心",
                                "uri": f"https://liff.line.me/{settings.LINE_LIFF_ID}/notifications"
                            }
                        }
                    ]
                }
            }
        }
