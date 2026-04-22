#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用工具调用基类

提供统一的工具调用接口，减少代码重复。
包含：
- 异步 subprocess 调用
- 超时处理
- 错误处理
- 输出解析
- 并发控制

使用方式:
    class MyToolAdapter(BaseToolAdapter):
        async def call_my_tool(self, target: str):
            cmd = f"mytool -t {target}"
            return await self.call_tool(
                cmd=cmd,
                timeout=300,
                parse_func=self._parse_output
            )
"""

import asyncio
import logging
from typing import Callable, Dict, List, Any, Optional
from utils.logger import setup_logger


class BaseToolAdapter:
    """工具调用基类"""
    
    def __init__(self, max_concurrent: int = 3):
        """
        初始化基类
        
        Args:
            max_concurrent: 最大并发数（默认 3）
        """
        self.logger = setup_logger(self.__class__.__name__)
        # 信号量限制并发数
        self._semaphore = asyncio.Semaphore(max_concurrent)
    
    async def call_tool(
        self,
        cmd: str,
        timeout: int = 300,
        parse_func: Optional[Callable[[str, str], List[Dict[str, Any]]]] = None,
        shell: bool = True
    ) -> List[Dict[str, Any]]:
        """
        通用工具调用方法
        
        Args:
            cmd: 要执行的命令
            timeout: 超时时间（秒，默认 300）
            parse_func: 输出解析函数，接收 (stdout, stderr) 返回解析结果
            shell: 是否使用 shell 执行（默认 True）
        
        Returns:
            解析后的结果列表
        """
        try:
            self.logger.debug(f"执行命令：{cmd}")
            
            # 创建 subprocess
            if shell:
                process = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
            else:
                process = await asyncio.create_subprocess_exec(
                    *cmd.split(),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
            
            try:
                # 等待完成，带超时
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                # 超时强制终止进程
                self.logger.warning(f"命令执行超时：{cmd}")
                try:
                    process.kill()
                    await process.wait()
                except ProcessLookupError:
                    pass
                raise
            
            # 解码输出
            stdout_text = stdout.decode('utf-8', errors='replace')
            stderr_text = stderr.decode('utf-8', errors='replace')
            
            # 记录日志
            if process.returncode != 0:
                self.logger.warning(
                    f"命令返回码非 0: {process.returncode}, "
                    f"错误：{stderr_text[:200] if stderr_text else '无'}"
                )
            
            # 解析输出
            if parse_func:
                try:
                    return parse_func(stdout_text, stderr_text)
                except Exception as e:
                    self.logger.error(f"解析输出失败：{e}")
                    return []
            
            return []
            
        except asyncio.TimeoutError:
            self.logger.warning(f"工具调用超时：{cmd[:100]}")
            return []
        except FileNotFoundError:
            self.logger.error(f"工具未找到：{cmd.split()[0] if shell else cmd[0]}")
            return []
        except Exception as e:
            self.logger.error(f"工具调用失败：{e}")
            return []
    
    async def call_tool_with_retry(
        self,
        cmd: str,
        timeout: int = 300,
        parse_func: Optional[Callable] = None,
        max_retries: int = 2,
        retry_delay: int = 2,
        shell: bool = True
    ) -> List[Dict[str, Any]]:
        """
        带重试的工具调用
        
        Args:
            cmd: 要执行的命令
            timeout: 超时时间（秒）
            parse_func: 输出解析函数
            max_retries: 最大重试次数（默认 2）
            retry_delay: 重试延迟（秒，默认 2，指数退避）
            shell: 是否使用 shell 执行
        
        Returns:
            解析后的结果列表
        """
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                return await self.call_tool(
                    cmd=cmd,
                    timeout=timeout,
                    parse_func=parse_func,
                    shell=shell
                )
            except asyncio.TimeoutError:
                last_error = asyncio.TimeoutError()
                if attempt < max_retries:
                    wait_time = retry_delay * (2 ** attempt)  # 指数退避
                    self.logger.warning(
                        f"超时，{wait_time}秒后重试 ({attempt + 1}/{max_retries})"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(f"重试 {max_retries} 次后仍超时")
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    self.logger.warning(
                        f"失败，{retry_delay}秒后重试 ({attempt + 1}/{max_retries}): {e}"
                    )
                    await asyncio.sleep(retry_delay)
                else:
                    self.logger.error(f"重试 {max_retries} 次后仍失败：{e}")
        
        # 所有重试都失败
        self.logger.error(f"工具调用最终失败：{last_error}")
        return []
    
    async def execute_with_semaphore(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        在信号量保护下执行函数（限制并发）
        
        Args:
            func: 要执行的异步函数
            *args: 位置参数
            **kwargs: 关键字参数
        
        Returns:
            函数执行结果
        """
        async with self._semaphore:
            return await func(*args, **kwargs)
    
    async def gather_with_concurrency(
        self,
        coroutines: List,
        concurrency: Optional[int] = None
    ) -> List:
        """
        以指定并发数执行多个协程
        
        Args:
            coroutines: 协程列表
            concurrency: 并发数（None 表示使用默认值）
        
        Returns:
            结果列表
        """
        if concurrency is None:
            concurrency = self._semaphore._value
        
        semaphore = asyncio.Semaphore(concurrency)
        
        async def sem_coro(coro):
            async with semaphore:
                return await coro
        
        tasks = [sem_coro(coro) for coro in coroutines]
        return await asyncio.gather(*tasks, return_exceptions=True)
