import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from typing import List, Tuple, Callable, Any, Optional
from .logger import ModernLogger

class ParallelProcessor(ModernLogger):
    """Base class for parallel processing operations."""
    
    def __init__(self):
        super().__init__(name="ParallelProcessor")
    
    def determine_worker_count(self, workers: Optional[int] = None) -> int:
        """Determine optimal worker count if not specified."""
        if workers is None:
            return min(os.cpu_count() or 4, 8)
        return workers
    
    def create_batches(self, items: List[Any], batch_size: int) -> List[Tuple[List[int], List[Any]]]:
        """Split items into batches of given size."""
        total = len(items)
        batches: List[Tuple[List[int], List[Any]]] = []
        for i in range(0, total, batch_size):
            idxs = list(range(i, min(i + batch_size, total)))
            batch = [items[j] for j in idxs]
            batches.append((idxs, batch))
        return batches
    
    def process_with_retry(
        self,
        idx: int,
        item: Any,
        process_func: Callable,
        max_retries: int = 2,
        **kwargs
    ) -> Tuple[int, Any]:
        """Process a single item with retry and backoff."""
        retries = 0
        while True:
            try:
                result = process_func(item, **kwargs)
                return idx, result
            except Exception as e:
                retries += 1
                if retries > max_retries:
                    self.error(f"❌ [Item {idx}] Failed after {max_retries} retries: {e}")
                    return idx, None
                backoff = 0.5 * (2 ** retries)
                self.warning(f"⚠️ [Item {idx}] Retry {retries}/{max_retries} after {backoff:.1f}s")
                time.sleep(backoff)
    
    def process_batches(
        self,
        batches: List[Tuple[List[int], List[Any]]],
        workers: int,
        process_func: Callable,
        total_items: int,
        task_description: str = "Processing items",
        max_retries: int = 2,
        timeout: int = 180,
        **kwargs
    ) -> List[Any]:
        """
        Process all batches in parallel, showing a rich progress bar.
        """
        final_results: List[Optional[Any]] = [None] * total_items
        # 调用 ModernLogger.progress()
        progress, task_id = self.progress(total_items, task_description)
        
        with progress:
            completed = 0
            for idxs, batch in batches:
                with ThreadPoolExecutor(max_workers=workers) as executor:
                    futures = [
                        executor.submit(
                            self.process_with_retry,
                            idx,
                            item,
                            process_func,
                            max_retries,
                            **kwargs
                        )
                        for idx, item in zip(idxs, batch)
                    ]
                    for fut in as_completed(futures):
                        try:
                            idx, result = fut.result(timeout=timeout)
                            if result is not None:
                                final_results[idx] = result
                            completed += 1
                            progress.update(task_id, completed=completed)
                        except TimeoutError:
                            self.warning(f"⏱️ Task timed out after {timeout}s")
                            completed += 1
                            progress.update(task_id, completed=completed)
                        except Exception as e:
                            self.error(f"❌ Error in future: {e}")
                            completed += 1
                            progress.update(task_id, completed=completed)
        
        # 过滤失败的 None
        return [r for r in final_results if r is not None]
    
    def parallel_process(
        self,
        items: List[Any],
        process_func: Callable,
        workers: Optional[int] = None,
        batch_size: int = 5,
        max_retries: int = 2,
        timeout: int = 180,
        task_description: str = "Processing items",
        **kwargs
    ) -> List[Any]:
        """
        High-level entry: determine workers, batch items, then process.
        """
        try:
            total = len(items)
            if total == 0:
                self.info("ℹ️ No items to process.")
                return []
            
            workers = self.determine_worker_count(workers)
            batches = self.create_batches(items, batch_size)
            return self.process_batches(
                batches=batches,
                workers=workers,
                process_func=process_func,
                total_items=total,
                task_description=task_description,
                max_retries=max_retries,
                timeout=timeout,
                **kwargs
            )
        except Exception as e:
            self.error(f"❌ Error during parallel processing: {e}")
            return []
