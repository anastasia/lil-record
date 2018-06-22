try:
    from .settings import *
except ImportError as e:
    if e.msg == "No module named 'settings.settings'":
        from .settings_base import *
    else:
        raise