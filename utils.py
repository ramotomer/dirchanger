import traceback
from functools import partial
from typing import Callable, Union, Type, Tuple, Any, TypeVar

from exceptions import DirChangerError


Return_T = TypeVar("Return_T")


def rpartial(func: Callable[[Any, ...], Return_T], *args: Any, **kwargs: Any) -> Callable[[Any, ...], Return_T]:
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


def run_as_user_shortcut(function: Callable[[], None], exceptions: Union[Type[Exception], Tuple[Type[Exception]]] = DirChangerError):
    try:
        function()
    except exceptions:
        traceback.print_exc()
        input("\n\npress enter to exit...")