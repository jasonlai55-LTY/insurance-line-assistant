from linebot.v3 import WebhookHandler
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
from app.core.config import settings

line_config = Configuration(access_token=settings.LINE_CHANNEL_ACCESS_TOKEN)
line_api_client = ApiClient(line_config)
messaging_api = MessagingApi(line_api_client)
line_webhook_handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)
