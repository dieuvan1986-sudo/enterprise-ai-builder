"""
Enterprise AI Builder
Kernel - Plugin Manager
Version: 0.2.0
"""

from kernel.plugin_loader import PluginLoader
from registry.plugin_registry import PluginRegistry


class PluginManager:
    """
    Quản lý toàn bộ vòng đời của Plugin.

    Sprint 1:
    - Discover Plugin
    - Đăng ký Plugin vào Registry

    Sprint 2:
    - Validate
    - Activate
    - Shutdown
    """

    def __init__(self, plugin_directory):
        self.loader = PluginLoader(plugin_directory)
        self.registry = PluginRegistry()

    def discover(self):
        """
        Discover tất cả Plugin và đăng ký vào Registry.
        """

        plugins = self.loader.discover()

        for plugin in plugins:
            self.registry.register(plugin)

        return self.registry.list()

    def list(self):
        """
        Trả về danh sách Plugin đã đăng ký.
        """

        return self.registry.list()

    def get(self, plugin_id):
        """
        Lấy Plugin theo ID.
        """

        return self.registry.get(plugin_id)

    def exists(self, plugin_id):
        """
        Kiểm tra Plugin có tồn tại hay không.
        """

        return self.registry.exists(plugin_id)

    def count(self):
        """
        Trả về số lượng Plugin.
        """

        return self.registry.count()
