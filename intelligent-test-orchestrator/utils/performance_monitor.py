"""
性能监控模块 - 实时性能指标收集和报告
"""

import time
import psutil
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict
import threading
from pathlib import Path
import json


class PerformanceMetrics:
    """性能指标收集器"""
    
    def __init__(self):
        """初始化性能监控"""
        self._metrics: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._lock = threading.RLock()
        self._start_time = time.time()
        self._process = psutil.Process(os.getpid())
    
    def record(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """记录指标
        
        Args:
            metric_name: 指标名称
            value: 指标值
            tags: 标签字典
        """
        with self._lock:
            record = {
                'timestamp': time.time(),
                'value': value,
                'tags': tags or {}
            }
            self._metrics[metric_name].append(record)
            
            # 限制每个指标的记录数（保留最近 1000 条）
            if len(self._metrics[metric_name]) > 1000:
                self._metrics[metric_name] = self._metrics[metric_name][-1000:]
    
    def get_metric(self, metric_name: str, 
                   start_time: Optional[float] = None,
                   end_time: Optional[float] = None) -> List[Dict[str, Any]]:
        """获取指标数据"""
        with self._lock:
            records = self._metrics.get(metric_name, [])
            
            if start_time:
                records = [r for r in records if r['timestamp'] >= start_time]
            if end_time:
                records = [r for r in records if r['timestamp'] <= end_time]
            
            return records
    
    def get_stats(self, metric_name: str) -> Dict[str, Any]:
        """获取指标统计信息"""
        records = self.get_metric(metric_name)
        
        if not records:
            return {'count': 0}
        
        values = [r['value'] for r in records]
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'sum': sum(values),
            'latest': values[-1] if values else None
        }
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """获取所有指标的统计信息"""
        with self._lock:
            return {
                name: self.get_stats(name)
                for name in self._metrics.keys()
            }
    
    def clear(self) -> None:
        """清空所有指标"""
        with self._lock:
            self._metrics.clear()
    
    def export_to_json(self, filepath: str) -> None:
        """导出指标到 JSON 文件"""
        with self._lock:
            data = {
                'exported_at': datetime.now().isoformat(),
                'uptime_seconds': time.time() - self._start_time,
                'metrics': dict(self._metrics)
            }
            
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)


class SystemMonitor:
    """系统资源监控"""
    
    def __init__(self):
        """初始化系统监控"""
        self._process = psutil.Process(os.getpid())
    
    def get_cpu_usage(self) -> float:
        """获取 CPU 使用率"""
        return self._process.cpu_percent(interval=0.1)
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """获取内存使用情况"""
        mem_info = self._process.memory_info()
        
        return {
            'rss_mb': mem_info.rss / 1024 / 1024,  # 物理内存 (MB)
            'vms_mb': mem_info.vms / 1024 / 1024,  # 虚拟内存 (MB)
            'percent': self._process.memory_percent()
        }
    
    def get_disk_usage(self, path: str = "/") -> Dict[str, Any]:
        """获取磁盘使用情况"""
        disk = psutil.disk_usage(path)
        
        return {
            'total_gb': disk.total / 1024 / 1024 / 1024,
            'used_gb': disk.used / 1024 / 1024 / 1024,
            'free_gb': disk.free / 1024 / 1024 / 1024,
            'percent': disk.percent
        }
    
    def get_thread_count(self) -> int:
        """获取线程数"""
        return self._process.num_threads()
    
    def get_connection_count(self) -> int:
        """获取网络连接数"""
        try:
            connections = self._process.connections()
            return len(connections)
        except psutil.AccessDenied:
            return 0
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        return {
            'cpu_count': psutil.cpu_count(),
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_total_gb': psutil.virtual_memory().total / 1024 / 1024 / 1024,
            'memory_available_gb': psutil.virtual_memory().available / 1024 / 1024 / 1024,
            'memory_percent': psutil.virtual_memory().percent
        }


class PerformanceMonitor:
    """性能监控管理器"""
    
    _instance: Optional['PerformanceMonitor'] = None
    
    def __new__(cls) -> 'PerformanceMonitor':
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化性能监控管理器"""
        if not hasattr(self, '_initialized'):
            self._metrics = PerformanceMetrics()
            self._system_monitor = SystemMonitor()
            self._monitoring = False
            self._monitor_thread: Optional[threading.Thread] = None
            self._monitor_interval = 10  # 秒
            self._initialized = True
    
    @property
    def metrics(self) -> PerformanceMetrics:
        """获取性能指标收集器"""
        return self._metrics
    
    def start_monitoring(self, interval: int = 10) -> None:
        """启动自动监控
        
        Args:
            interval: 监控间隔（秒）
        """
        if self._monitoring:
            return
        
        self._monitor_interval = interval
        self._monitoring = True
        
        def monitor_loop():
            while self._monitoring:
                # 记录系统资源使用情况
                cpu_usage = self._system_monitor.get_cpu_usage()
                self._metrics.record('cpu_usage', cpu_usage)
                
                memory = self._system_monitor.get_memory_usage()
                self._metrics.record('memory_rss', memory['rss_mb'])
                self._metrics.record('memory_percent', memory['percent'])
                
                self._metrics.record('thread_count', self._system_monitor.get_thread_count())
                self._metrics.record('connection_count', self._system_monitor.get_connection_count())
                
                time.sleep(self._monitor_interval)
        
        self._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitor_thread.start()
    
    def stop_monitoring(self) -> None:
        """停止自动监控"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
    
    def record_execution_time(self, func_name: str, duration: float, 
                             success: bool = True, tags: Optional[Dict[str, str]] = None) -> None:
        """记录函数执行时间"""
        exec_tags = {'function': func_name, 'success': str(success)}
        if tags:
            exec_tags.update(tags)
        
        self._metrics.record(f'{func_name}_duration', duration, exec_tags)
        self._metrics.record(f'{func_name}_success', 1 if success else 0, exec_tags)
    
    def record_tool_execution(self, tool_name: str, duration: float, 
                             target: str, success: bool = True) -> None:
        """记录工具执行情况"""
        tags = {
            'tool': tool_name,
            'target': target[:50],  # 限制长度
            'success': str(success)
        }
        
        self._metrics.record(f'tool_{tool_name}_duration', duration, tags)
        self._metrics.record(f'tool_{tool_name}_success', 1 if success else 0, tags)
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        cpu_stats = self._metrics.get_stats('cpu_usage')
        memory_stats = self._metrics.get_stats('memory_percent')
        
        # 获取最新系统状态
        system_info = self._system_monitor.get_system_info()
        process_memory = self._system_monitor.get_memory_usage()
        
        # 判断健康状态
        health = 'healthy'
        issues = []
        
        if cpu_stats.get('latest', 0) > 90:
            health = 'unhealthy'
            issues.append(f"CPU 使用率过高：{cpu_stats['latest']:.1f}%")
        elif cpu_stats.get('latest', 0) > 70:
            health = 'warning'
            issues.append(f"CPU 使用率较高：{cpu_stats['latest']:.1f}%")
        
        if process_memory['percent'] > 90:
            health = 'unhealthy'
            issues.append(f"内存使用率过高：{process_memory['percent']:.1f}%")
        elif process_memory['percent'] > 70:
            if health != 'unhealthy':
                health = 'warning'
            issues.append(f"内存使用率较高：{process_memory['percent']:.1f}%")
        
        return {
            'status': health,
            'issues': issues,
            'system': {
                'cpu_percent': system_info['cpu_percent'],
                'memory_total_gb': system_info['memory_total_gb'],
                'memory_available_gb': system_info['memory_available_gb']
            },
            'process': {
                'cpu_percent': self._system_monitor.get_cpu_usage(),
                'memory_mb': process_memory['rss_mb'],
                'memory_percent': process_memory['percent'],
                'threads': self._system_monitor.get_thread_count(),
                'connections': self._system_monitor.get_connection_count()
            },
            'metrics': {
                'cpu_avg': cpu_stats.get('avg', 0),
                'memory_avg': memory_stats.get('avg', 0)
            },
            'uptime_seconds': time.time() - self._metrics._start_time
        }
    
    def get_report(self) -> Dict[str, Any]:
        """生成性能报告"""
        return {
            'generated_at': datetime.now().isoformat(),
            'uptime_seconds': time.time() - self._metrics._start_time,
            'health': self.get_health_status(),
            'metrics': self._metrics.get_all_metrics(),
            'system': self._system_monitor.get_system_info()
        }
    
    def export_report(self, filepath: str) -> None:
        """导出性能报告"""
        report = self.get_report()
        
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
    
    def print_status(self) -> None:
        """打印当前状态"""
        health = self.get_health_status()
        
        print("\n" + "=" * 60)
        print("  性能监控状态")
        print("=" * 60)
        
        # 健康状态
        status_icon = "✅" if health['status'] == 'healthy' else "⚠️" if health['status'] == 'warning' else "❌"
        print(f"\n{status_icon} 健康状态：{health['status'].upper()}")
        
        if health['issues']:
            print("\n⚠️  问题:")
            for issue in health['issues']:
                print(f"   - {issue}")
        
        # 系统资源
        print(f"\n📊 系统资源:")
        print(f"   CPU: {health['process']['cpu_percent']:.1f}%")
        print(f"   内存：{health['process']['memory_mb']:.1f} MB ({health['process']['memory_percent']:.1f}%)")
        print(f"   线程：{health['process']['threads']}")
        print(f"   连接：{health['process']['connections']}")
        
        # 运行时间
        uptime = health['uptime_seconds']
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        print(f"\n⏱️  运行时间：{hours:02d}:{minutes:02d}:{seconds:02d}")
        
        print("=" * 60 + "\n")


# 性能监控装饰器
def monitored(func_name: Optional[str] = None):
    """性能监控装饰器
    
    Args:
        func_name: 函数名称，None 则使用函数名
    
    Returns:
        装饰器函数
    """
    def decorator(func):
        name = func_name or func.__name__
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            monitor = PerformanceMonitor()
            start_time = time.time()
            success = True
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                monitor.record_execution_time(name, duration, success)
        
        return wrapper
    return decorator


# 便捷函数
def get_performance_monitor() -> PerformanceMonitor:
    """获取性能监控管理器实例"""
    return PerformanceMonitor()


def start_auto_monitoring(interval: int = 10) -> None:
    """启动自动监控"""
    monitor = get_performance_monitor()
    monitor.start_monitoring(interval)


def stop_auto_monitoring() -> None:
    """停止自动监控"""
    monitor = get_performance_monitor()
    monitor.stop_monitoring()


def print_performance_status() -> None:
    """打印性能状态"""
    monitor = get_performance_monitor()
    monitor.print_status()
