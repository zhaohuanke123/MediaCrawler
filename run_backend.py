import sys
import asyncio
import uvicorn

if __name__ == "__main__":
    # 强制 Windows 使用 ProactorEventLoop (支持子进程，Playwright 需要这个)
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    print("正在启动 MediaCrawler 后端服务...")
    print("注意：已强制启用 WindowsProactorEventLoopPolicy 以支持 Playwright")

    # 启动 uvicorn
    uvicorn.run(
        "backend.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        loop="asyncio"
    )
