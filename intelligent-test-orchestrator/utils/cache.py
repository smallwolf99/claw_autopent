"""
缓存模块 - 内存缓存和 Redis 缓存支持
"""

import time
import hashlib
import json
import pickle
from typing import Any, Dict, Optional, Callable, TypeVar, ParamSpec
from functools import wraps
from datetime import datetime, timedelta
from pathlib import Path
import threading


T = TypeVar('T')
P = ParamSpec('P')


class CacheEntry:
    """缓存条目"""
    
    def __init__(self, value: Any, ttl: Optional[int] = None):
        """初始化缓存条目
        
        Args:
            value: 缓存值
            ttl: 生存时间（秒），None 表示永不过期
        """
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
        self.hits = 0
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.ttl is None:
            return False
        return (time.time() - self.created_at) > self.ttl
    
    def get(self) -> Any:
        """获取值并增加命中计数"""
        self.hits += 1
        return self.value


class MemoryCache:
    """内存缓存实现"""
    
    def __init__(self, max_size: int = 1000, default_ttl: Optional[int] = 3600):
        """初始化内存缓存
        
        Args:
            max_size: 最大缓存条目数
            default_ttl: 默认生存时间（秒）
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expirations': 0
        }
    
    def _generate_key(self, key: str, *args, **kwargs) -> str:
        """生成缓存键"""
        if not args and not kwargs:
            return key
        
        # 创建参数哈希 - 将 args 转换为列表以保证序列化一致性
        params = {
            'args': list(args),
            'kwargs': kwargs
        }
        params_str = json.dumps(params, default=str, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()
        
        return f"{key}:{params_hash}"
    
    def get(self, key: str, *args, **kwargs) -> Optional[Any]:
        """获取缓存值"""
        cache_key = self._generate_key(key, *args, **kwargs)
        
        with self._lock:
            entry = self._cache.get(cache_key)
            
            if entry is None:
                self._stats['misses'] += 1
                return None
            
            if entry.is_expired():
                del self._cache[cache_key]
                self._stats['expirations'] += 1
                self._stats['misses'] += 1
                return None
            
            self._stats['hits'] += 1
            return entry.get()
    
    def set(self, key: str, value: Any, *args, ttl: Optional[int] = None, **kwargs) -> None:
        """设置缓存值"""
        cache_key = self._generate_key(key, *args, **kwargs)
        
        with self._lock:
            # 如果缓存已满，删除最旧的条目
            if len(self._cache) >= self.max_size and cache_key not in self._cache:
                self._evict_oldest()
            
            actual_ttl = ttl if ttl is not None else self.default_ttl
            self._cache[cache_key] = CacheEntry(value, actual_ttl)
    
    def delete(self, key: str, *args, **kwargs) -> bool:
        """删除缓存值"""
        cache_key = self._generate_key(key, *args, **kwargs)
        
        with self._lock:
            if cache_key in self._cache:
                del self._cache[cache_key]
                return True
            return False
    
    def clear(self) -> None:
        """清空缓存"""
        with self._lock:
            self._cache.clear()
    
    def _evict_oldest(self) -> None:
        """删除最旧的条目（LRU 策略）"""
        if not self._cache:
            return
        
        # 找到最少使用的条目
        oldest_key = min(
            self._cache.keys(),
            key=lambda k: (self._cache[k].created_at, -self._cache[k].hits)
        )
        del self._cache[oldest_key]
        self._stats['evictions'] += 1
    
    def cleanup_expired(self) -> int:
        """清理过期条目"""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self._cache[key]
                self._stats['expirations'] += 1
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        with self._lock:
            total = self._stats['hits'] + self._stats['misses']
            hit_rate = (self._stats['hits'] / total * 100) if total > 0 else 0
            
            return {
                **self._stats,
                'total_requests': total,
                'hit_rate': f"{hit_rate:.2f}%",
                'current_size': len(self._cache),
                'max_size': self.max_size
            }
    
    def __len__(self) -> int:
        """获取缓存大小"""
        return len(self._cache)
    
    def __contains__(self, key: str) -> bool:
        """检查键是否存在"""
        return self.get(key) is not None


class FileCache:
    """文件缓存（持久化）"""
    
    def __init__(self, cache_dir: str, default_ttl: Optional[int] = 86400):
        """初始化文件缓存
        
        Args:
            cache_dir: 缓存目录
            default_ttl: 默认生存时间（秒）
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl
        self._lock = threading.RLock()
    
    def _get_file_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        # 使用哈希避免文件名过长
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        file_path = self._get_file_path(key)
        
        if not file_path.exists():
            return None
        
        with self._lock:
            try:
                with open(file_path, 'rb') as f:
                    data = pickle.load(f)
                
                # 检查过期
                if 'ttl' in data and data['ttl'] is not None:
                    age = time.time() - data['created_at']
                    if age > data['ttl']:
                        file_path.unlink()
                        return None
                
                return data['value']
            except Exception:
                return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存值"""
        file_path = self._get_file_path(key)
        
        with self._lock:
            data = {
                'value': value,
                'created_at': time.time(),
                'ttl': ttl if ttl is not None else self.default_ttl
            }
            
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
    
    def delete(self, key: str) -> bool:
        """删除缓存值"""
        file_path = self._get_file_path(key)
        
        with self._lock:
            if file_path.exists():
                file_path.unlink()
                return True
            return False
    
    def clear(self) -> None:
        """清空缓存"""
        with self._lock:
            for file_path in self.cache_dir.glob("*.cache"):
                file_path.unlink()
    
    def cleanup_expired(self) -> int:
        """清理过期条目"""
        count = 0
        with self._lock:
            for file_path in self.cache_dir.glob("*.cache"):
                try:
                    with open(file_path, 'rb') as f:
                        data = pickle.load(f)
                    
                    if 'ttl' in data and data['ttl'] is not None:
                        age = time.time() - data['created_at']
                        if age > data['ttl']:
                            file_path.unlink()
                            count += 1
                except Exception:
                    file_path.unlink()
                    count += 1
        
        return count


class CacheManager:
    """缓存管理器 - 统一管理内存和文件缓存"""
    
    _instance: Optional['CacheManager'] = None
    
    def __new__(cls) -> 'CacheManager':
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化缓存管理器"""
        if not hasattr(self, '_initialized'):
            self._memory_cache = MemoryCache(max_size=1000, default_ttl=3600)
            self._file_cache: Optional[FileCache] = None
            self._use_file_cache = False
            self._initialized = True
    
    @property
    def memory_cache(self) -> MemoryCache:
        """获取内存缓存"""
        return self._memory_cache
    
    def enable_file_cache(self, cache_dir: str, default_ttl: int = 86400) -> None:
        """启用文件缓存"""
        self._file_cache = FileCache(cache_dir, default_ttl)
        self._use_file_cache = True
    
    def get(self, key: str, *args, **kwargs) -> Optional[Any]:
        """获取缓存值（优先内存，其次文件）"""
        # 先查内存缓存
        value = self._memory_cache.get(key, *args, **kwargs)
        if value is not None:
            return value
        
        # 再查文件缓存
        if self._use_file_cache and self._file_cache:
            value = self._file_cache.get(key)
            if value is not None:
                # 回写到内存缓存
                self._memory_cache.set(key, value, *args, **kwargs)
                return value
        
        return None
    
    def set(self, key: str, value: Any, *args, ttl: Optional[int] = None, 
            use_file: bool = False, **kwargs) -> None:
        """设置缓存值"""
        # 总是写入内存缓存
        self._memory_cache.set(key, value, *args, ttl=ttl, **kwargs)
        
        # 可选写入文件缓存
        if use_file and self._use_file_cache and self._file_cache:
            self._file_cache.set(key, value, ttl)
    
    def delete(self, key: str, *args, **kwargs) -> None:
        """删除缓存值"""
        self._memory_cache.delete(key, *args, **kwargs)
        if self._use_file_cache and self._file_cache:
            self._file_cache.delete(key)
    
    def clear(self) -> None:
        """清空所有缓存"""
        self._memory_cache.clear()
        if self._use_file_cache and self._file_cache:
            self._file_cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        stats = {
            'memory_cache': self._memory_cache.get_stats(),
            'file_cache_enabled': self._use_file_cache
        }
        
        if self._use_file_cache and self._file_cache:
            cache_files = list(self._file_cache.cache_dir.glob("*.cache"))
            stats['file_cache_size'] = len(cache_files)
        
        return stats
    
    def cleanup(self) -> None:
        """清理过期缓存"""
        self._memory_cache.cleanup_expired()
        if self._use_file_cache and self._file_cache:
            self._file_cache.cleanup_expired()


# 缓存装饰器
def cached(cache: Optional[MemoryCache] = None, ttl: Optional[int] = None):
    """缓存装饰器
    
    Args:
        cache: 缓存实例，None 则使用全局缓存
        ttl: 生存时间（秒）
    
    Returns:
        装饰器函数
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # 获取缓存实例
            cache_instance = cache or CacheManager().memory_cache
            
            # 生成缓存键
            cache_key = func.__name__
            
            # 尝试从缓存获取
            result = cache_instance.get(cache_key, *args, **kwargs)
            if result is not None:
                return result
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 写入缓存
            cache_instance.set(cache_key, result, *args, ttl=ttl, **kwargs)
            
            return result
        
        return wrapper
    return decorator


# 便捷函数
def get_cache_manager() -> CacheManager:
    """获取缓存管理器实例"""
    return CacheManager()


def create_cache(max_size: int = 1000, default_ttl: int = 3600) -> MemoryCache:
    """创建内存缓存"""
    return MemoryCache(max_size, default_ttl)


def create_file_cache(cache_dir: str, default_ttl: int = 86400) -> FileCache:
    """创建文件缓存"""
    return FileCache(cache_dir, default_ttl)
