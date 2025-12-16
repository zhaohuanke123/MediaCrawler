import time
import json
import requests
from . import config

# 全局缓存 Token，避免频繁请求
TOKEN_CACHE = {
    "token": None,
    "expire_time": 0
}

def get_tenant_access_token():
    """
    获取飞书机器人的访问凭证 (自动管理过期)
    """
    global TOKEN_CACHE
    # 如果 Token 存在且没过期（预留 10 分钟缓冲），直接返回
    if TOKEN_CACHE["token"] and time.time() < TOKEN_CACHE["expire_time"] - 600:
        return TOKEN_CACHE["token"]

    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    payload = {
        "app_id": config.APP_ID,
        "app_secret": config.APP_SECRET
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload)
        data = resp.json()
        if data.get("code") == 0:
            TOKEN_CACHE["token"] = data["tenant_access_token"]
            # expire 通常是 7200 秒，我们记录绝对过期时间
            TOKEN_CACHE["expire_time"] = time.time() + data["expire"]
            print("🔄 更新 Tenant Access Token 成功")
            return data["tenant_access_token"]
        else:
            print(f"❌ 获取 Token 失败: {data}")
            return None
    except Exception as e:
        print(f"❌ 获取 Token 异常: {e}")
        return None

def send_feishu_message(chat_id, content):
    """
    发送消息给飞书用户
    """
    token = get_tenant_access_token()
    if not token:
        return

    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    params = {"receive_id_type": "chat_id"} # 明确指定接收 ID 类型为会话 ID
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    body = {
        "receive_id": chat_id, # 直接回复到这个会话
        "msg_type": "text",
        "content": json.dumps({"text": content}) # content 必须是 JSON 字符串
    }

    try:
        resp = requests.post(url, params=params, headers=headers, json=body)
        print(f"✅ 回复消息结果: {resp.status_code} - {resp.json().get('msg')}")
    except Exception as e:
        print(f"❌ 发送消息异常: {e}")

def send_feishu_markdown(chat_id, md_text):
    """
    发送 Markdown 消息卡片给飞书用户
    """
    token = get_tenant_access_token()
    if not token:
        return

    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    params = {"receive_id_type": "chat_id"}
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    # === 关键修改：构建卡片结构 ===
    # 飞书卡片只支持部分 Markdown 语法（被称为 Lark MD）
    card_content = {
        "config": {
            "wide_screen_mode": True  # 开启宽屏模式，防止表格/长文被压缩
        },
        "header": {
            "template": "blue",       # 标题颜色：blue, red, turquoise, etc.
            "title": {
                "content": "📝 AI 视频总结", # 卡片标题
                "tag": "plain_text"
            }
        },
        "elements": [
            {
                "tag": "markdown",    # 使用 markdown 组件
                "content": md_text    # 你的 AI 总结内容放这里
            },
            {
                "tag": "note",        # 底部小注（可选）
                "elements": [
                    {
                        "tag": "plain_text",
                        "content": "由 Python 自动生成"
                    }
                ]
            }
        ]
    }

    body = {
        "receive_id": chat_id,
        "msg_type": "interactive",  # 类型必须是 interactive
        "content": json.dumps(card_content) # content 必须是卡片 JSON 的字符串
    }

    try:
        resp = requests.post(url, params=params, headers=headers, json=body)
        print(f"✅ 发送卡片结果: {resp.status_code} - {resp.json().get('msg')}")
    except Exception as e:
        print(f"❌ 发送异常: {e}")
