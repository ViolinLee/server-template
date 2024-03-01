import time
import warnings
from functools import wraps


def timer(func):
    """ 函数运行时长计算装饰器

    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} executed in {end_time - start_time} seconds")
        return result

    return wrapper


def retry(exceptions, tries=5, delay=2):
    """ 重试装饰器，当原函数由于指定的异常而失败时，会重试指定的次数，每次重试之间有固定的间隔时间。

    :param exceptions: 一个异常类或异常类元组，当这些异常被捕获时，函数将被重试。
    :param tries: 重试次数。
    :param delay: 每次重试之间的延迟时间（秒）。
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(tries):
                try:
                    result = func(*args, **kwargs)
                    return result
                except exceptions as e:
                    print(f"Error: {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)
            raise Exception(f"{func.__name__} failed after {tries} retries.")
        return wrapper
    return decorator


def ignore_errors(ignore=True):
    """ 异常传递控制装饰器

    当ignore为True,装饰器会捕获异常但忽略它；当 ignore 为 False 时，装饰器会将异常传递给上层调用者。
    :param ignore:
    :return:
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if not ignore:
                    raise
                else:
                    warnings.warn(str(e))
        return wrapper
    return decorator


if __name__ == '__main__':
    # timer unit test
    @timer
    def example_function(duration):
        time.sleep(duration)
        return "Function completed"

    print(example_function(2))

    # retry unit test
    @retry(exceptions=(Exception,), tries=3, delay=2)
    def test_function():
        print("Trying...")
        # 这里可以放置可能失败的代码
        raise Exception("Something went wrong!")

    test_function()
