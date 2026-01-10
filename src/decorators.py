import asyncio
import inspect
from time import perf_counter
from functools import wraps
from collections.abc import Awaitable
from typing import overload, ParamSpec, TypeVar, Callable

from loguru import logger

R = TypeVar("R")
P = ParamSpec("P")


@overload
def with_timer(func: Callable[P, R]) -> Callable[P, R]: ...

@overload
def with_timer(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]: ...

def with_timer(func: Callable[P, R] | Callable[P, Awaitable[R]]) -> Callable[P, R] | Callable[P, Awaitable[R]]:
    if inspect.iscoroutinefunction(func):
        @wraps(func)
        async def _wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                start_time = perf_counter()
                result = await func(*args, **kwargs)
                return result
            finally:
                end_time = perf_counter()
                logger.info(f"Function {func.__name__} took {end_time - start_time:.4f} seconds to run")
        return _wrapper

    @wraps(func)
    def _wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            start_time = perf_counter()
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = perf_counter()
            logger.info(f"Function {func.__name__} took {end_time - start_time:.4f} seconds to run")
    return _wrapper



def with_semaphore(semaphore: asyncio.Semaphore):
    def _decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @wraps(func)
        async def _wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            async with semaphore:
                return await func(*args, **kwargs)
        return _wrapper
    return _decorator