"""
Enterprise AI Builder
Registry - Plugin Registry
Version: 0.1.0
"""


class PluginRegistry:
    """
    Quản lý danh sách Plugin đã được nạp.

    Chức năng:
    - Đăng ký Plugin
    - Kiểm tra Plugin tồn tại
    - Lấy Plugin theo ID
    - Liệt kê toàn bộ Plugin
    """

    def __init__(self):
        self._plugins = {}

    def register(self, plugin):
        """
        Đăng ký một Plugin.
        """

        plugin_id = plugin.get("id")

        if not plugin_id:
            raise ValueError("Plugin must have an 'id'.")

        self._plugins[plugin_id] = plugin

    def get(self, plugin_id):
        """
        Lấy Plugin theo ID.
        """

        return self._plugins.get(plugin_id)

    def exists(self, plugin_id):
        """
        Kiểm tra Plugin đã tồn tại hay chưa.
        """

        return plugin_id in self._plugins

    def list(self):
        """
        Trả về danh sách tất cả Plugin.
        """

        return list(self._plugins.values())

    def count(self):
        """
        Trả về số lượng Plugin.
        """

        return len(self._plugins)
