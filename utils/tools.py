import time
from functools import wraps
from utils.log import Logger


def retry(max_attempts=3, delay=0.2, exceptions=(Exception,)):
    """
    重试装饰器
    :param max_attempts: 最大重试次数
    :param delay: 每次重试之间的等待时间（秒）
    :param exceptions: 需要捕获并重试的异常类型（元组）
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempts += 1
                    if attempts == max_attempts:
                        Logger.error(f"函数{func.__name__}达到最大重试次数 ({max_attempts})，最后一次错误: {e}")
                        raise  # 最终还是失败，抛出异常
                    
                    Logger.warning(f"检测到异常: {e}。函数{func.__name__}正在进行第 {attempts} 次重试...")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator