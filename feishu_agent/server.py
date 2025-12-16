from fastapi import FastAPI, Request, BackgroundTasks
import uvicorn
import json
import re
import asyncio
import sys
import os
import subprocess
from .bot import send_feishu_message, send_feishu_markdown

app = FastAPI()

def run_crawler_cli(video_id: str):
    """
    在独立进程中运行爬虫
    """
    python_exe = sys.executable
    # 假设 run_crawler_task.py 在项目根目录
    script_path = os.path.join(os.getcwd(), "run_crawler_task.py")
    
    cmd = [python_exe, script_path, video_id]
    
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

async def run_bilibili_crawler(video_id: str):
    """
    运行 Bilibili 爬虫抓取指定视频
    """
    print(f"🕷️ 启动 B站爬虫，目标视频 ID: {video_id}")
    
    # 【关键点】使用 to_thread 将同步的 subprocess 放到线程池运行
    # 这样既不会阻塞 FastAPI，也不受 EventLoop 类型的限制
    output = await asyncio.to_thread(run_crawler_cli, video_id)
    
    # 检查输出中是否有成功标志
    if "Crawler finished successfully" in output:
        print(f"✅ B站视频 {video_id} 抓取完成")
        
        # 尝试提取 AI 总结
        summary_match = re.search(r"__SUMMARY_START__\n(.*?)\n__SUMMARY_END__", output, re.DOTALL)
        if summary_match:
            summary_content = summary_match.group(1)
            return {"success": True, "summary": summary_content}
        
        return {"success": True, "summary": None}
    else:
        print(f"❌ B站爬虫运行可能失败，输出片段: {output[-200:] if output else 'None'}")
        return {"success": False, "summary": None}

async def ai_process_and_reply(chat_id, user_text):
    """
    处理用户消息并回复
    """
    print(f"⏳ 开始后台处理任务，用户内容: {user_text}")
    
    # 1. 检查是否包含 B站 BV 号
    # BV号格式通常为 BV1xxxxxxxxx
    bv_pattern = r"(BV[a-zA-Z0-9]{10})"
    match = re.search(bv_pattern, user_text)
    
    if match:
        video_id = match.group(1)
        send_feishu_message(chat_id, f"🤖 检测到 B站视频 ID: {video_id}，正在启动爬虫抓取并进行 AI 总结...")
        
        result = await run_bilibili_crawler(video_id)
        
        if result["success"]:
            if result["summary"]:
                # 使用卡片消息发送 Markdown 总结
                send_feishu_markdown(chat_id, result["summary"])
                # 另外发送一条简单的文本确认
                send_feishu_message(chat_id, f"✅ B站视频 {video_id} 处理完成，总结如上。")
            else:
                msg = f"✅ B站视频 {video_id} 抓取完成！数据已保存。\n\n⚠️ 未生成 AI 总结 (可能未配置 API Key 或视频下载失败)。"
                send_feishu_message(chat_id, msg)
        else:
            send_feishu_message(chat_id, f"❌ B站视频 {video_id} 抓取失败，请检查服务器日志。")
            
    else:
        # 2. 普通消息处理
        # === 这里写你的耗时逻辑 (比如调用 ChatGPT / 爬虫) ===
        await asyncio.sleep(2) # 模拟处理了 2 秒
        reply_content = f"🤖 我收到了你的消息：\n「{user_text}」\n\n这是服务器异步处理后的回复！"
        send_feishu_message(chat_id, reply_content)

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
