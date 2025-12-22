from fastapi import FastAPI, Request, BackgroundTasks
import uvicorn
import json
import re
import asyncio
import sys
import os
import subprocess
from .bot import send_feishu_message, send_feishu_markdown
from tools.social_media_link_parser import SocialMediaLinkParser

app = FastAPI()
link_parser = SocialMediaLinkParser()

def run_crawler_cli(platform: str, video_id: str):
    """
    在独立进程中运行爬虫
    """
    python_exe = sys.executable
    # 假设 run_crawler_task.py 在项目根目录
    script_path = os.path.join(os.getcwd(), "run_crawler_task.py")
    
    cmd = [python_exe, script_path, platform, video_id]
    
    print(f"🚀 开始调用爬虫进程: {' '.join(cmd)}")
    
    output_lines = []
    try:
        # 使用 Popen 实时获取输出
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, # 将 stderr 合并到 stdout
            text=True,
            encoding='utf-8',
            bufsize=1 # 行缓冲
        )
        
        # 实时读取输出并打印
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                print(line.strip()) # 打印到当前终端
                output_lines.append(line)
                
        return_code = process.poll()
        full_output = "".join(output_lines)
        
        if return_code != 0:
            print(f"❌ 爬虫进程异常退出，代码: {return_code}")
            return f"Error: Process exited with code {return_code}\nOutput:\n{full_output}"
            
        print("✅ 爬虫运行结束")
        return full_output

    except Exception as e:
        print(f"❌ 调用异常: {e}")
        return f"Exception: {e}"

async def run_platform_crawler(platform: str, video_id: str):
    """
    运行指定平台的爬虫抓取指定视频
    """
    print(f"🕷️ 启动 {platform} 爬虫，目标 ID: {video_id}")
    
    # 【关键点】使用 to_thread 将同步的 subprocess 放到线程池运行
    # 这样既不会阻塞 FastAPI，也不受 EventLoop 类型的限制
    output = await asyncio.to_thread(run_crawler_cli, platform, video_id)
    
    # 检查输出中是否有成功标志
    if "Crawler finished successfully" in output:
        print(f"✅ {platform} 视频 {video_id} 抓取完成")
        
        # 尝试提取 AI 总结
        summary_match = re.search(r"__SUMMARY_START__\n(.*?)\n__SUMMARY_END__", output, re.DOTALL)
        if summary_match:
            summary_content = summary_match.group(1)
            return {"success": True, "summary": summary_content}
        
        return {"success": True, "summary": None}
    else:
        print(f"❌ {platform} 爬虫运行可能失败，输出片段: {output[-200:] if output else 'None'}")
        return {"success": False, "summary": None}

def extract_id_from_url(platform, url):
    if platform == "bilibili":
        match = re.search(r"(BV[a-zA-Z0-9]+)", url)
        return match.group(1) if match else None
    elif platform == "douyin":
        match = re.search(r"/video/(\d+)", url)
        return match.group(1) if match else None
    elif platform == "xiaohongshu":
        match = re.search(r"/(?:item|explore)/([a-f0-9]+)", url)
        return match.group(1) if match else None
    return None

async def ai_process_and_reply(chat_id, user_text):
    """
    处理用户消息并回复
    """
    print(f"⏳ 开始后台处理任务，用户内容: {user_text}")
    
    # 使用 SocialMediaLinkParser 解析链接
    parse_result = link_parser.parse(user_text)
    platform = parse_result.get("platform")
    target_url = parse_result.get("target_url")
    
    # 标记是否已处理，避免重复处理
    processed = False

    if platform != "unknown" and target_url:
        video_id = extract_id_from_url(platform, target_url)
        
        if video_id:
            # 映射 platform 名称到 run_crawler_task.py 接受的参数 (bili, dy, xhs)
            platform_arg = ""
            if platform == "bilibili":
                platform_arg = "bili"
            elif platform == "douyin":
                platform_arg = "dy"
            elif platform == "xiaohongshu":
                platform_arg = "xhs"
            
            send_feishu_message(chat_id, f"🤖 检测到 {platform} 链接，ID: {video_id}，正在启动爬虫抓取并进行 AI 总结...")
            
            result = await run_platform_crawler(platform_arg, video_id)
            
            if result["success"]:
                if result["summary"]:
                    send_feishu_markdown(chat_id, result["summary"])
                    send_feishu_message(chat_id, f"✅ 视频 {video_id} 处理完成，总结如上。")
                else:
                    send_feishu_message(chat_id, "✅ 视频抓取成功，但未生成总结（可能是因为没有视频文件或 AI 接口未配置）。")
            else:
                send_feishu_message(chat_id, "❌ 视频抓取失败，请检查日志。")
            
            processed = True
        else:
            send_feishu_message(chat_id, f"⚠️ 识别到 {platform} 链接，但无法提取 ID。URL: {target_url}")
            processed = True # 虽然失败但已尝试处理

    # 如果上面的解析器没有处理（例如没有 URL，只有 BV 号），尝试后备逻辑
    if not processed:
        # 尝试旧的 B站 BV 号匹配逻辑作为后备
        bv_pattern = r"(BV[a-zA-Z0-9]{10})"
        match = re.search(bv_pattern, user_text)
        
        if match:
            video_id = match.group(1)
            send_feishu_message(chat_id, f"🤖 检测到 B站视频 ID: {video_id}，正在启动爬虫抓取并进行 AI 总结...")
            result = await run_platform_crawler("bili", video_id)
            if result["success"]:
                if result["summary"]:
                    send_feishu_markdown(chat_id, result["summary"])
                    send_feishu_message(chat_id, f"✅ 视频 {video_id} 处理完成，总结如上。")
                else:
                    send_feishu_message(chat_id, "✅ 视频抓取成功，但未生成总结。")
            else:
                send_feishu_message(chat_id, "❌ 视频抓取失败。")
        else:
            # 既不是链接也不是 BV 号，当作普通聊天消息
            # await asyncio.sleep(2) # 模拟处理
            # reply_content = f"🤖 我收到了你的消息：\n「{user_text}」\n\n请发送 B站/抖音/小红书 的分享链接或 B站 BV 号。"
            # send_feishu_message(chat_id, reply_content)
            print("⚠️ 未检测到支持的社交媒体链接或 ID")

# ---------------- 主路由 ----------------

@app.post("/feishu/callback")
async def feishu_webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    
    # 1. 处理 URL 校验
    if data.get("type") == "url_verification":
        return {"challenge": data.get("challenge")}

    # 2. 处理消息事件
    header = data.get("header", {})
    if header.get("event_type") == "im.message.receive_v1":
        event = data.get("event", {})
        
        # 获取必要的 ID 和内容
        chat_id = event.get("message", {}).get("chat_id")
        message_content = event.get("message", {}).get("content", "")
        
        try:
            content_dict = json.loads(message_content)
            text = content_dict.get("text", "")
            
            # 【核心步骤】将耗时任务加入后台队列，FastAPI 会立即返回 200 OK
            # 注意：不要在这里 await，直接 add_task
            if chat_id and text:
                background_tasks.add_task(ai_process_and_reply, chat_id, text)
                
        except Exception as e:
            print(f"解析消息失败: {e}")

    # 3. 无论后台任务是否成功，这里必须迅速返回 success 防止飞书重试
    return {"msg": "success"}
