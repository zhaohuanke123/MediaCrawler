# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tools/cdp_browser.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1
#

# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。


import os
import asyncio
import socket
import httpx
import signal
import atexit
from typing import Optional, Dict, Any
from playwright.async_api import Browser, BrowserContext, Playwright

import config
from tools.browser_launcher import BrowserLauncher
from tools import utils


class CDPBrowserManager:
    """
    CDP浏览器管理器，负责启动和管理通过CDP连接的浏览器
    """

    def __init__(self):
        self.launcher = BrowserLauncher()
        self.browser: Optional[Browser] = None
        self.browser_context: Optional[BrowserContext] = None
        self.debug_port: Optional[int] = None
        self._cleanup_registered = False

    def _register_cleanup_handlers(self):
        """
        注册清理处理器，确保程序退出时清理浏览器进程
        """
        if self._cleanup_registered:
            return

        def sync_cleanup():
            """同步清理函数，用于atexit"""
            if self.launcher and self.launcher.browser_process:
                utils.logger.info("[CDPBrowserManager] atexit: 清理浏览器进程")
                self.launcher.cleanup()

        # 注册atexit清理
        atexit.register(sync_cleanup)

        # 注册信号处理器
        def signal_handler(signum, frame):
            """信号处理器"""
            utils.logger.info(f"[CDPBrowserManager] 收到信号 {signum}，清理浏览器进程")
            if self.launcher and self.launcher.browser_process:
                self.launcher.cleanup()
            # 重新引发KeyboardInterrupt以便正常退出流程
            if signum == signal.SIGINT:
                raise KeyboardInterrupt

        # 注册SIGINT (Ctrl+C) 和 SIGTERM
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        self._cleanup_registered = True
        utils.logger.info("[CDPBrowserManager] 清理处理器已注册")

    async def launch_and_connect(
        self,
        playwright: Playwright,
        playwright_proxy: Optional[Dict] = None,
        user_agent: Optional[str] = None,
        headless: bool = False,
    ) -> BrowserContext:
        """
        启动浏览器并通过CDP连接
        """
        try:
            # 1. 检测浏览器路径
            browser_path = await self._get_browser_path()

            # 2. 尝试清理默认端口上的僵尸进程
            await self._try_cleanup_existing_browser(config.CDP_DEBUG_PORT, playwright)

            # 3. 获取可用端口
            self.debug_port = self.launcher.find_available_port(config.CDP_DEBUG_PORT)

            # 4. 启动浏览器
            await self._launch_browser(browser_path, headless)

            # 5. 注册清理处理器（确保异常退出时也能清理）
            self._register_cleanup_handlers()

            # 6. 通过CDP连接
            await self._connect_via_cdp(playwright)

            # 7. 创建浏览器上下文
            browser_context = await self._create_browser_context(
                playwright_proxy, user_agent
            )

            self.browser_context = browser_context
            return browser_context

        except Exception as e:
            utils.logger.error(f"[CDPBrowserManager] CDP浏览器启动失败: {e}")
            await self.cleanup()
            raise

    async def _try_cleanup_existing_browser(self, port: int, playwright: Playwright):
        """
        尝试清理指定端口上已存在的浏览器实例
        """
        if self._is_port_available(port):
            return

        utils.logger.info(f"[CDPBrowserManager] 端口 {port} 被占用，尝试清理僵尸浏览器进程...")
        
        try:
            # 1. 尝试通过CDP协议关闭
            try:
                # 尝试获取 WebSocket URL
                ws_url = await self._get_browser_websocket_url(port)
                
                # 尝试连接并关闭
                utils.logger.info(f"[CDPBrowserManager] 正在连接到旧实例并执行关闭...")
                browser = await playwright.chromium.connect_over_cdp(ws_url)
                if browser.is_connected():
                    await browser.close()
                    utils.logger.info(f"[CDPBrowserManager] 旧浏览器实例已关闭(通过CDP)")
                    
                    # 等待端口释放
                    for _ in range(10):
                        if self._is_port_available(port):
                            utils.logger.info(f"[CDPBrowserManager] 端口 {port} 已释放")
                            return
                        await asyncio.sleep(0.5)
            except Exception as e:
                utils.logger.warning(f"[CDPBrowserManager] 通过CDP清理旧浏览器失败: {e}")

            # 2. 如果端口仍然被占用，尝试通过系统命令强制杀进程 (Windows)
            if not self._is_port_available(port):
                 utils.logger.info(f"[CDPBrowserManager] 端口 {port} 仍被占用，尝试通过系统命令查找并清理...")
                 await self._force_kill_process_by_port(port)
                 
        except Exception as e:
            utils.logger.warning(f"[CDPBrowserManager] 清理旧浏览器实例失败: {e}")

    async def _force_kill_process_by_port(self, port: int):
        """通过端口强制杀进程 (主要针对 Windows)"""
        import sys
        if sys.platform == "win32":
            try:
                # 查找占用端口的 PID
                # netstat -ano | findstr :<port>
                cmd = f"netstat -ano | findstr :{port}"
                proc = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, _ = await proc.communicate()
                output = stdout.decode('gbk', errors='ignore') # Windows 默认编码可能为 gbk
                
                pids = set()
                for line in output.splitlines():
                    parts = line.strip().split()
                    if len(parts) > 4:
                        # 端口匹配检查，防止误杀
                        # netstat 输出类似: TCP 127.0.0.1:9222 0.0.0.0:0 LISTENING 1234
                        local_addr = parts[1]
                        if f":{port}" in local_addr:
                            pid = parts[-1]
                            if pid.isdigit() and int(pid) > 0:
                                pids.add(pid)
                
                if not pids:
                    utils.logger.info(f"[CDPBrowserManager] 未找到占用端口 {port} 的进程PID")
                    return

                for pid in pids:
                    utils.logger.info(f"[CDPBrowserManager] 正在强制结束进程 PID: {pid}")
                    # taskkill /F /PID <pid>
                    kill_cmd = f"taskkill /F /PID {pid}"
                    await asyncio.create_subprocess_shell(
                        kill_cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                
                # 再次等待端口释放
                for _ in range(10):
                     if self._is_port_available(port):
                         utils.logger.info(f"[CDPBrowserManager] 端口 {port} 已释放(通过taskkill)")
                         return
                     await asyncio.sleep(0.5)

            except Exception as e:
                 utils.logger.error(f"[CDPBrowserManager] 强制结束进程失败: {e}")
        else:
            # Linux/Mac 实现 (使用 lsof 或 fuser)
            pass # 暂未实现，主要针对用户环境 Windows

    def _is_port_available(self, port: int) -> bool:
        """检查端口是否可用"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False

    async def _get_browser_path(self) -> str:
        """
        获取浏览器路径
        """
        # 优先使用用户自定义路径
        if config.CUSTOM_BROWSER_PATH and os.path.isfile(config.CUSTOM_BROWSER_PATH):
            utils.logger.info(
                f"[CDPBrowserManager] 使用自定义浏览器路径: {config.CUSTOM_BROWSER_PATH}"
            )
            return config.CUSTOM_BROWSER_PATH

        # 自动检测浏览器路径
        browser_paths = self.launcher.detect_browser_paths()

        if not browser_paths:
            raise RuntimeError(
                "未找到可用的浏览器。请确保已安装Chrome或Edge浏览器，"
                "或在配置文件中设置CUSTOM_BROWSER_PATH指定浏览器路径。"
            )

        browser_path = browser_paths[0]  # 使用第一个找到的浏览器
        browser_name, browser_version = self.launcher.get_browser_info(browser_path)

        utils.logger.info(
            f"[CDPBrowserManager] 检测到浏览器: {browser_name} ({browser_version})"
        )
        utils.logger.info(f"[CDPBrowserManager] 浏览器路径: {browser_path}")

        return browser_path

    async def _test_cdp_connection(self, debug_port: int) -> bool:
        """
        测试CDP连接是否可用
        """
        try:
            # 简单的socket连接测试
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                result = s.connect_ex(("localhost", debug_port))
                if result == 0:
                    utils.logger.info(
                        f"[CDPBrowserManager] CDP端口 {debug_port} 可访问"
                    )
                    return True
                else:
                    utils.logger.warning(
                        f"[CDPBrowserManager] CDP端口 {debug_port} 不可访问"
                    )
                    return False
        except Exception as e:
            utils.logger.warning(f"[CDPBrowserManager] CDP连接测试失败: {e}")
            return False

    async def _launch_browser(self, browser_path: str, headless: bool):
        """
        启动浏览器进程
        """
        # 设置用户数据目录（如果启用了保存登录状态）
        user_data_dir = None
        if config.SAVE_LOGIN_STATE:
            user_data_dir = os.path.join(
                os.getcwd(),
                "browser_data",
                f"cdp_{config.USER_DATA_DIR % config.PLATFORM}",
            )
            os.makedirs(user_data_dir, exist_ok=True)
            utils.logger.info(f"[CDPBrowserManager] 用户数据目录: {user_data_dir}")

        # 启动浏览器
        self.launcher.browser_process = self.launcher.launch_browser(
            browser_path=browser_path,
            debug_port=self.debug_port,
            headless=headless,
            user_data_dir=user_data_dir,
        )

        # 等待浏览器准备就绪
        if not self.launcher.wait_for_browser_ready(
            self.debug_port, config.BROWSER_LAUNCH_TIMEOUT
        ):
            raise RuntimeError(f"浏览器在 {config.BROWSER_LAUNCH_TIMEOUT} 秒内未能启动")

        # 额外等待一秒让CDP服务完全启动
        await asyncio.sleep(1)

        # 测试CDP连接
        if not await self._test_cdp_connection(self.debug_port):
            utils.logger.warning(
                "[CDPBrowserManager] CDP连接测试失败，但将继续尝试连接"
            )

    async def _get_browser_websocket_url(self, debug_port: int) -> str:
        """
        获取浏览器的WebSocket连接URL
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://localhost:{debug_port}/json/version", timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    ws_url = data.get("webSocketDebuggerUrl")
                    if ws_url:
                        utils.logger.info(
                            f"[CDPBrowserManager] 获取到浏览器WebSocket URL: {ws_url}"
                        )
                        return ws_url
                    else:
                        raise RuntimeError("未找到webSocketDebuggerUrl")
                else:
                    raise RuntimeError(f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            utils.logger.error(f"[CDPBrowserManager] 获取WebSocket URL失败: {e}")
            raise

    async def _connect_via_cdp(self, playwright: Playwright):
        """
        通过CDP连接到浏览器
        """
        try:
            # 获取正确的WebSocket URL
            ws_url = await self._get_browser_websocket_url(self.debug_port)
            utils.logger.info(f"[CDPBrowserManager] 正在通过CDP连接到浏览器: {ws_url}")

            # 使用Playwright的connectOverCDP方法连接
            self.browser = await playwright.chromium.connect_over_cdp(ws_url)

            if self.browser.is_connected():
                utils.logger.info("[CDPBrowserManager] 成功连接到浏览器")
                utils.logger.info(
                    f"[CDPBrowserManager] 浏览器上下文数量: {len(self.browser.contexts)}"
                )
            else:
                raise RuntimeError("CDP连接失败")

        except Exception as e:
            utils.logger.error(f"[CDPBrowserManager] CDP连接失败: {e}")
            raise

    async def _create_browser_context(
        self, playwright_proxy: Optional[Dict] = None, user_agent: Optional[str] = None
    ) -> BrowserContext:
        """
        创建或获取浏览器上下文
        """
        if not self.browser:
            raise RuntimeError("浏览器未连接")

        # 获取现有上下文或创建新的上下文
        contexts = self.browser.contexts

        if contexts:
            # 使用现有的第一个上下文
            browser_context = contexts[0]
            utils.logger.info("[CDPBrowserManager] 使用现有的浏览器上下文")
        else:
            # 创建新的上下文
            context_options = {
                "viewport": {"width": 1920, "height": 1080},
                "accept_downloads": True,
            }

            # 设置用户代理
            if user_agent:
                context_options["user_agent"] = user_agent
                utils.logger.info(f"[CDPBrowserManager] 设置用户代理: {user_agent}")

            # 注意：CDP模式下代理设置可能不生效，因为浏览器已经启动
            if playwright_proxy:
                utils.logger.warning(
                    "[CDPBrowserManager] 警告: CDP模式下代理设置可能不生效，"
                    "建议在浏览器启动前配置系统代理或浏览器代理扩展"
                )

            browser_context = await self.browser.new_context(**context_options)
            utils.logger.info("[CDPBrowserManager] 创建新的浏览器上下文")

        return browser_context

    async def add_stealth_script(self, script_path: str = "libs/stealth.min.js"):
        """
        添加反检测脚本
        """
        if self.browser_context and os.path.exists(script_path):
            try:
                await self.browser_context.add_init_script(path=script_path)
                utils.logger.info(
                    f"[CDPBrowserManager] 已添加反检测脚本: {script_path}"
                )
            except Exception as e:
                utils.logger.warning(f"[CDPBrowserManager] 添加反检测脚本失败: {e}")

    async def add_cookies(self, cookies: list):
        """
        添加Cookie
        """
        if self.browser_context:
            try:
                await self.browser_context.add_cookies(cookies)
                utils.logger.info(f"[CDPBrowserManager] 已添加 {len(cookies)} 个Cookie")
            except Exception as e:
                utils.logger.warning(f"[CDPBrowserManager] 添加Cookie失败: {e}")

    async def get_cookies(self) -> list:
        """
        获取当前Cookie
        """
        if self.browser_context:
            try:
                cookies = await self.browser_context.cookies()
                return cookies
            except Exception as e:
                utils.logger.warning(f"[CDPBrowserManager] 获取Cookie失败: {e}")
                return []
        return []

    async def cleanup(self, force: bool = False):
        """
        清理资源

        Args:
            force: 是否强制清理浏览器进程（忽略AUTO_CLOSE_BROWSER配置）
        """
        try:
            # 关闭浏览器上下文
            if self.browser_context:
                try:
                    # 检查上下文是否已经关闭
                    # 尝试获取页面列表，如果失败说明已经关闭
                    try:
                        pages = self.browser_context.pages
                        if pages is not None:
                            await self.browser_context.close()
                            utils.logger.info("[CDPBrowserManager] 浏览器上下文已关闭")
                    except:
                        utils.logger.debug("[CDPBrowserManager] 浏览器上下文已经被关闭")
                except Exception as context_error:
                    # 只在错误不是因为已关闭时才记录警告
                    error_msg = str(context_error).lower()
                    if "closed" not in error_msg and "disconnected" not in error_msg:
                        utils.logger.warning(
                            f"[CDPBrowserManager] 关闭浏览器上下文失败: {context_error}"
                        )
                    else:
                        utils.logger.debug(f"[CDPBrowserManager] 浏览器上下文已关闭: {context_error}")
                finally:
                    self.browser_context = None

            # 断开浏览器连接
            if self.browser:
                try:
                    # 检查浏览器是否仍然连接
                    if self.browser.is_connected():
                        await self.browser.close()
                        utils.logger.info("[CDPBrowserManager] 浏览器连接已断开")
                    else:
                        utils.logger.debug("[CDPBrowserManager] 浏览器连接已经断开")
                except Exception as browser_error:
                    # 只在错误不是因为已关闭时才记录警告
                    error_msg = str(browser_error).lower()
                    if "closed" not in error_msg and "disconnected" not in error_msg:
                        utils.logger.warning(
                            f"[CDPBrowserManager] 关闭浏览器连接失败: {browser_error}"
                        )
                    else:
                        utils.logger.debug(f"[CDPBrowserManager] 浏览器连接已关闭: {browser_error}")
                finally:
                    self.browser = None

            # 关闭浏览器进程
            # force=True 时强制关闭，忽略AUTO_CLOSE_BROWSER配置
            # 这用于处理异常退出或手动清理的情况
            if force or config.AUTO_CLOSE_BROWSER:
                if self.launcher and self.launcher.browser_process:
                    self.launcher.cleanup()
                else:
                    utils.logger.debug("[CDPBrowserManager] 没有需要清理的浏览器进程")
            else:
                utils.logger.info(
                    "[CDPBrowserManager] 浏览器进程保持运行（AUTO_CLOSE_BROWSER=False）"
                )

        except Exception as e:
            utils.logger.error(f"[CDPBrowserManager] 清理资源时出错: {e}")

    def is_connected(self) -> bool:
        """
        检查是否已连接到浏览器
        """
        return self.browser is not None and self.browser.is_connected()

    async def get_browser_info(self) -> Dict[str, Any]:
        """
        获取浏览器信息
        """
        if not self.browser:
            return {}

        try:
            version = self.browser.version
            contexts_count = len(self.browser.contexts)

            return {
                "version": version,
                "contexts_count": contexts_count,
                "debug_port": self.debug_port,
                "is_connected": self.is_connected(),
            }
        except Exception as e:
            utils.logger.warning(f"[CDPBrowserManager] 获取浏览器信息失败: {e}")
            return {}
