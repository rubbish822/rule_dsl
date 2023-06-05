import functools
import inspect
import typing


def fac(
    title: str = '',
    description: str = '',
    enabled: bool = True,
    ctype: str = None,
    rtype: typing.Any = None,
    **kwargs,
):
    if callable(title):
        func = title
        func_name = func.__name__
        func.__dict__['_dict'] = {
            'title': func_name,
            'description': func_name,
            'type': 'fac',
            'enabled': enabled,
            'ctype': ctype,
            'rtype': rtype,
            **kwargs,
        }

        @functools.wraps(func)
        def wrap(*args, **kwargs):
            return func(*args, **kwargs)

        return wrap

    def decorator_function(func):
        func_name = func.__name__
        func.__dict__['_dict'] = {
            'title': title or func_name,
            'description': description or func_name,
            'type': 'fac',
            'enabled': enabled,
            'ctype': ctype,
            'rtype': rtype,
            **kwargs,
        }

        @functools.wraps(func)
        def wrap(*args, **kwargs):
            return func(*args, **kwargs)

        return wrap

    return decorator_function


def fun(
    title: str = '',
    description: str = '',
    enabled: bool = True,
    ctype: str = None,
    rtype: typing.Any = None,
    **kwargs,
):
    if callable(title):
        func = title
        func_name = func.__name__
        func.__dict__['_dict'] = {
            'title': func_name,
            'description': func_name,
            'type': 'fun',
            'enabled': enabled,
            'ctype': ctype,
            'rtype': rtype,
            **kwargs,
        }

        @functools.wraps(func)
        def wrap(*args, **kwargs):
            return func(*args, **kwargs)

        return wrap

    def decorator_function(func):
        func_name = func.__name__
        func.__dict__['_dict'] = {
            'title': title or func_name,
            'description': description or func_name,
            'type': 'fun',
            'enabled': enabled,
            'ctype': ctype,
            'rtype': rtype,
            **kwargs,
        }

        @functools.wraps(func)
        def wrap(*args, **kwargs):
            return func(*args, **kwargs)

        return wrap

    return decorator_function


def act(
    title: str = '',
    description: str = '',
    enabled: bool = True,
    ctype: str = None,
    rtype: typing.Any = None,
    **kwargs,
):
    if callable(title):
        func = title
        func_name = func.__name__
        func.__dict__['_dict'] = {
            'title': func_name,
            'description': func_name,
            'type': 'act',
            'enabled': enabled,
            'ctype': ctype,
            'rtype': rtype,
            **kwargs,
        }

        @functools.wraps(func)
        def wrap(*args, **kwargs):
            return func(*args, **kwargs)

        return wrap

    def decorator_function(func):
        func_name = func.__name__
        func.__dict__['_dict'] = {
            'title': title or func_name,
            'description': description or func_name,
            'type': 'act',
            'enabled': enabled,
            'ctype': ctype,
            'rtype': rtype,
            **kwargs,
        }

        @functools.wraps(func)
        def wrap(*args, **kwargs):
            return func(*args, **kwargs)

        return wrap

    return decorator_function


DSL_MAP = {}


def collect_register_fat(dsl_imports: list) -> list:
    """
    收集所有注册的@fac、@fun、@act函数
    Args:
        dsl_imports (list): ['dsl.runner.mysql', 'dsl.runner.pg', 'dsl.runner.redis']

    Returns:
        list: [{'name': '@fac.user_is_admin', 'title': 'user_is_admin', 'description': 'user_is_admin', 'func_type': 'fac', 'type': 'redis', 'enabled': True}]
    """
    from .dsl import BaseCommonDSL, BaseDSL

    for dsl_import in dsl_imports:
        __import__(dsl_import)
    sub_classes = BaseCommonDSL.__subclasses__() + BaseDSL.__subclasses__()
    all_register = []
    for sub_class in sub_classes:
        DSL_MAP[sub_class.type_] = sub_class
        all_function_list = inspect.getmembers(sub_class, predicate=inspect.isfunction)
        for function_tuple in all_function_list:
            function = function_tuple[-1]
            _dict = function.__dict__.get('_dict')
            if _dict:
                data = {
                    'name': f'@{_dict["type"]}.{function.__name__}',
                    'title': _dict['title'],
                    'description': _dict['description'],
                    'func_type': _dict['type'],
                    'type': sub_class.type_,
                    'enabled': _dict['enabled'],
                    'ctype': _dict['ctype'],
                    **_dict,
                }
                all_register.append(data)
    return all_register
