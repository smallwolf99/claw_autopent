"""
内存优化模块 - 使用生成器和迭代器优化大数据处理
"""

from typing import Iterator, List, Dict, Any, Callable, Optional
import json
from pathlib import Path


class VulnerabilityStream:
    """漏洞数据流 - 使用生成器处理大量漏洞数据"""
    
    def __init__(self, vulnerabilities: List[Dict[str, Any]]):
        """初始化漏洞流"""
        self.vulnerabilities = vulnerabilities
    
    def filter(self, predicate: Callable[[Dict[str, Any]], bool]) -> 'VulnerabilityStream':
        """过滤漏洞"""
        self.vulnerabilities = [v for v in self.vulnerabilities if predicate(v)]
        return self
    
    def map(self, func: Callable[[Dict[str, Any]], Dict[str, Any]]) -> 'VulnerabilityStream':
        """转换漏洞数据"""
        self.vulnerabilities = [func(v) for v in self.vulnerabilities]
        return self
    
    def sort(self, key: Callable[[Dict[str, Any]], Any], reverse: bool = True) -> 'VulnerabilityStream':
        """排序漏洞"""
        self.vulnerabilities.sort(key=key, reverse=reverse)
        return self
    
    def limit(self, n: int) -> 'VulnerabilityStream':
        """限制数量"""
        self.vulnerabilities = self.vulnerabilities[:n]
        return self
    
    def group_by(self, key_func: Callable[[Dict[str, Any]], str]) -> Dict[str, List[Dict[str, Any]]]:
        """分组"""
        groups = {}
        for vuln in self.vulnerabilities:
            key = key_func(vuln)
            if key not in groups:
                groups[key] = []
            groups[key].append(vuln)
        return groups
    
    def to_list(self) -> List[Dict[str, Any]]:
        """转换为列表"""
        return self.vulnerabilities
    
    def to_dict_list(self, key_func: Callable[[Dict[str, Any]], str]) -> List[Dict[str, Any]]:
        """转换为字典列表"""
        return [{key_func(v): v} for v in self.vulnerabilities]
    
    def count(self) -> int:
        """计数"""
        return len(self.vulnerabilities)
    
    def sum(self, key_func: Callable[[Dict[str, Any]], float]) -> float:
        """求和"""
        return sum(key_func(v) for v in self.vulnerabilities)
    
    def avg(self, key_func: Callable[[Dict[str, Any]], float]) -> float:
        """求平均"""
        if not self.vulnerabilities:
            return 0.0
        return self.sum(key_func) / len(self.vulnerabilities)


def vulnerability_generator(vulnerabilities: List[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
    """漏洞生成器 - 惰性加载"""
    for vuln in vulnerabilities:
        yield vuln


def batch_generator(items: List[Any], batch_size: int) -> Iterator[List[Any]]:
    """分批生成器 - 大数据分批处理"""
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]


def file_line_generator(filepath: str) -> Iterator[str]:
    """文件行生成器 - 逐行读取大文件"""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在：{filepath}")
    
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            yield line.rstrip('\n')


def json_lines_generator(filepath: str) -> Iterator[Dict[str, Any]]:
    """JSON Lines 文件生成器 - 逐行解析 JSON"""
    for line in file_line_generator(filepath):
        if line.strip():
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def chunked_file_reader(filepath: str, chunk_size: int = 100) -> Iterator[List[str]]:
    """分块读取文件 - 每次读取 chunk_size 行"""
    chunk = []
    for line in file_line_generator(filepath):
        chunk.append(line)
        if len(chunk) >= chunk_size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def memory_efficient_vulnerability_processor(
    vulnerabilities: List[Dict[str, Any]],
    process_func: Callable[[Dict[str, Any]], Dict[str, Any]],
    batch_size: int = 100
) -> Iterator[Dict[str, Any]]:
    """内存友好的漏洞处理器 - 分批处理"""
    for batch in batch_generator(vulnerabilities, batch_size):
        for vuln in batch:
            try:
                yield process_func(vuln)
            except Exception:
                continue


def streaming_aggregator(
    data_stream: Iterator[Dict[str, Any]],
    aggregations: Dict[str, Callable[[List[Dict[str, Any]]], Any]]
) -> Dict[str, Any]:
    """流式聚合器 - 边读取边聚合"""
    results = {}
    buffer = []
    buffer_size = 100
    
    for item in data_stream:
        buffer.append(item)
        
        if len(buffer) >= buffer_size:
            for agg_name, agg_func in aggregations.items():
                if agg_name not in results:
                    results[agg_name] = []
                results[agg_name].append(agg_func(buffer))
            buffer = []
    
    # 处理剩余数据
    if buffer:
        for agg_name, agg_func in aggregations.items():
            if agg_name not in results:
                results[agg_name] = []
            results[agg_name].append(agg_func(buffer))
    
    return results


def deduplicate_generator(items: Iterator[Any]) -> Iterator[Any]:
    """去重生成器 - 保持顺序"""
    seen = set()
    for item in items:
        item_hash = hash(str(item)) if not isinstance(item, (int, str, float)) else item
        if item_hash not in seen:
            seen.add(item_hash)
            yield item


def filter_and_transform_generator(
    items: Iterator[Any],
    filter_func: Callable[[Any], bool],
    transform_func: Callable[[Any], Any]
) -> Iterator[Any]:
    """过滤和转换组合生成器"""
    for item in items:
        if filter_func(item):
            yield transform_func(item)


def merge_sorted_generators(
    generators: List[Iterator[Any]],
    key_func: Callable[[Any], Any]
) -> Iterator[Any]:
    """合并多个有序生成器"""
    import heapq
    
    # 初始化堆
    heap = []
    for i, gen in enumerate(generators):
        try:
            item = next(gen)
            heapq.heappush(heap, (key_func(item), i, item, gen))
        except StopIteration:
            pass
    
    # 合并
    while heap:
        _, gen_idx, item, gen = heapq.heappop(heap)
        yield item
        
        try:
            next_item = next(gen)
            heapq.heappush(heap, (key_func(next_item), gen_idx, next_item, gen))
        except StopIteration:
            pass


class ResourceEfficientProcessor:
    """资源高效处理器"""
    
    def __init__(self, max_memory_mb: int = 1024):
        """初始化处理器"""
        self.max_memory_mb = max_memory_mb
        self.processed_count = 0
    
    def process_large_dataset(
        self,
        data: List[Any],
        process_func: Callable[[Any], Any],
        chunk_size: int = 1000
    ) -> Iterator[Any]:
        """处理大数据集 - 分块处理"""
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            for item in chunk:
                try:
                    result = process_func(item)
                    self.processed_count += 1
                    yield result
                except Exception:
                    continue
            
            # 强制垃圾回收
            if self.processed_count % 10000 == 0:
                import gc
                gc.collect()
    
    def process_stream(
        self,
        stream: Iterator[Any],
        process_func: Callable[[Any], Any],
        error_handler: Optional[Callable[[Exception], None]] = None
    ) -> Iterator[Any]:
        """处理数据流"""
        for item in stream:
            try:
                yield process_func(item)
                self.processed_count += 1
            except Exception as e:
                if error_handler:
                    error_handler(e)
                continue


# 便捷函数
def create_vulnerability_stream(vulnerabilities: List[Dict[str, Any]]) -> VulnerabilityStream:
    """创建漏洞数据流"""
    return VulnerabilityStream(vulnerabilities)


def process_in_batches(
    items: List[Any],
    process_func: Callable[[Any], Any],
    batch_size: int = 100
) -> Iterator[Any]:
    """分批处理"""
    for batch in batch_generator(items, batch_size):
        for item in batch:
            yield process_func(item)


def read_large_file_efficiently(filepath: str, chunk_size: int = 100) -> Iterator[List[str]]:
    """高效读取大文件"""
    return chunked_file_reader(filepath, chunk_size)
