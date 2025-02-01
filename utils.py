import traceback
from contextlib import contextmanager
from functools import partial
from typing import Callable, Union, Type, Tuple, Any, TypeVar

Return_T = TypeVar("Return_T")


def rpartial(func: Callable, *args: Any, **kwargs: Any) -> Callable:
    """
    Like functools.partial but recursive.
    Example:

        my_par = rpartial(foo, rpartial(bar, 2))

        my_par()  # equivalent to calling `foo(bar(2))`
    """
    def returned():
        args_ =  tuple(arg() if isinstance(arg, partial) else arg for arg in args)
        kwargs_ = {kw: arg() if isinstance(arg, partial) else arg for kw, arg in kwargs.items()}
        return func(*args_, **kwargs_)

    return partial(returned)


@contextmanager
def user_friendly_errors(exceptions: Union[Type[Exception], Tuple[Type[Exception]]] = Exception):
    try:
        yield None
    except exceptions:
        traceback.print_exc()
        input("\n\npress enter to exit...")
    finally:
        pass