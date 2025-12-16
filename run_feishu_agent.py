import uvicorn
import sys
import asyncio

if __name__ == "__main__":
    # 强制 Windows 使用 ProactorEventLoop (支持子进程，Playwright 需要这个)
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    print("正在启动 Feishu Agent 服务...")
    
    uvicorn.run(
        "feishu_agent.server:app", 
        host="0.0.0.0", 
        port=8080, 
        reload=True
    )
