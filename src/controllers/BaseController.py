from helpers.config import get_settings


class BaseController:
    size_scale = 1024 * 1024  # 1 MB in bytes

    def __init__(self):
        self.app_settings = get_settings()