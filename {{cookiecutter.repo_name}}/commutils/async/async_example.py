"""
协程是一种协议，用于定义异步函数。协程本身不包含执行的上下文信息，需将协程对象实例化为任务才能执行。
协程必须通过 asyncio.run()，asyncio.create_task()，或 asyncio.ensure_future() 这样的函数转换为任务才能被事件循环执行。
"""

import asyncio


"""
asyncio.run() 是 Python 3.7 中引入的一个函数，它可以方便地运行一个异步任务并返回其结果。
它接受一个异步函数作为参数，并在运行时创建一个新的 asyncio 事件循环。这使得编写异步代码变得更加容易。

注意: 在调用"asyncio.run"后直接调用会报错"RuntimeError: There is no current event loop in thread 'MainThread'.",解决方案：
    1、不要在asyncio.get_event_loop().xxx之前调用asyncio.run
    2、调用asyncio.run之后新建一个event_loop
"""


async def my_coroutine1():
    await asyncio.sleep(1)
    return 'Done!'

result = asyncio.run(my_coroutine1())
print(result)


"""
@asyncio.coroutine 是一个装饰器，可用于将普通函数转换为协程。使用它可以使普通函数更容易地与 asyncio 一起使用。
它接受一个普通函数作为参数，并返回一个协程对象。
"""


@asyncio.coroutine
def my_coroutine2():
    yield from asyncio.sleep(1)
    return 'Done!'


# loop = asyncio.get_event_loop()
loop = asyncio.new_event_loop()  # 由于前面调用过asyncio.run
result = loop.run_until_complete(my_coroutine2())
print(result)


"""
@asyncio.ensure_future 是一个装饰器，可用于将函数或协程转换为 Future 对象。
Future 是 asyncio 中的一个任务对象，可以看作是协程的上下文管理器，它包含了协程的执行状态，例如是否完成、是否出错等
"""


async def task1():
    print("Task 1 started")
    await asyncio.sleep(2)
    print("Task 1 completed")
    return 'Task 1 result'


async def task2():
    print("Task 2 started")
    await asyncio.sleep(1)
    print("Task 2 completed")
    return 'Task 2 result'


async def main():
    # 使用 asyncio.ensure_future 包装两个异步任务
    future1 = asyncio.ensure_future(task1())
    future2 = asyncio.ensure_future(task2())

    # 等待两个任务完成
    await asyncio.gather(future1, future2)

    # 获取任务的结果
    result1 = future1.result()
    result2 = future2.result()

    print("Results:", result1, result2)


# 运行主函数
loop.run_until_complete(main())
