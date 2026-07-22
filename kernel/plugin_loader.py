"""
Enterprise AI Builder
Kernel - Plugin Loader
Version: 0.1.0
"""

from pathlib import Path


class PluginLoader:
    def __init__(self, plugin_directory):
        self.plugin_directory = Path(plugin_directory)

    def discover(self):
        """
        Tìm tất cả plugin.yaml trong thư mục plugins
        """
        plugins = []

        if not self.plugin_directory.exists():
            return plugins

        for manifest in self.plugin_directory.rglob("plugin.yaml"):

            plugin = self.read_manifest(manifest)

            if plugin:
                plugins.append(plugin)

        return plugins

    def read_manifest(self, manifest_path):
        """
        Đọc plugin.yaml theo dạng key: value đơn giản.
        Chưa dùng PyYAML để giữ Bootstrap tối giản.
        """

        data = {}

        try:

            with open(manifest_path, "r", encoding="utf-8") as f:

                for line in f:

                    line = line.strip()

                    if not line:
                        continue

                    if line.startswith("#"):
                        continue

                    if ":" not in line:
                        continue

                    key, value = line.split(":", 1)

                    data[key.strip()] = value.strip()

            data["path"] = str(manifest_path.parent)

            return data

        except Exception as e:

            return {
                "error": str(e),
                "path": str(manifest_path)
            }


if __name__ == "__main__":

    root = Path(__file__).resolve().parent.parent

    plugins = root / "plugins"

    loader = PluginLoader(plugins)

    results = loader.discover()

    print("=" * 60)

    print("Enterprise AI Builder Plugin Loader")

    print("=" * 60)

    if not results:

        print("No plugins found.")

    else:

        for plugin in results:

            print(f"Name    : {plugin.get('name')}")
            print(f"ID      : {plugin.get('id')}")
            print(f"Version : {plugin.get('version')}")
            print(f"Path    : {plugin.get('path')}")
            print("-" * 60)
