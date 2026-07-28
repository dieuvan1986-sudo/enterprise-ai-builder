"""
Tests for PluginManager
"""

from pathlib import Path

from kernel.plugin_manager import PluginManager


def create_sample_plugin(plugin_root: Path):
    """
    Tạo một plugin mẫu để kiểm thử.
    """

    plugin_dir = plugin_root / "creator-os"
    plugin_dir.mkdir(parents=True)

    manifest = plugin_dir / "plugin.yaml"

    manifest.write_text(
        "\n".join(
            [
                "id: creator-os",
                "name: Creator OS",
                "version: 0.1.0",
            ]
        ),
        encoding="utf-8",
    )


def test_plugin_discovery(tmp_path):
    """
    PluginManager phải discover được plugin.
    """

    plugin_root = tmp_path / "plugins"
    plugin_root.mkdir()

    create_sample_plugin(plugin_root)

    manager = PluginManager(str(plugin_root))

    plugins = manager.discover()

    assert len(plugins) == 1
    assert manager.count() == 1


def test_plugin_lookup(tmp_path):
    """
    Có thể lấy plugin theo ID.
    """

    plugin_root = tmp_path / "plugins"
    plugin_root.mkdir()

    create_sample_plugin(plugin_root)

    manager = PluginManager(str(plugin_root))
    manager.discover()

    assert manager.exists("creator-os")

    plugin = manager.get("creator-os")

    assert plugin["id"] == "creator-os"
    assert plugin["name"] == "Creator OS"
    assert plugin["version"] == "0.1.0"


def test_plugin_list(tmp_path):
    """
    Registry phải trả về đúng danh sách plugin.
    """

    plugin_root = tmp_path / "plugins"
    plugin_root.mkdir()

    create_sample_plugin(plugin_root)

    manager = PluginManager(str(plugin_root))
    manager.discover()

    plugins = manager.list()

    assert isinstance(plugins, list)
    assert len(plugins) == 1


def test_empty_plugin_directory(tmp_path):
    """
    Thư mục rỗng không được gây lỗi.
    """

    plugin_root = tmp_path / "plugins"
    plugin_root.mkdir()

    manager = PluginManager(str(plugin_root))

    plugins = manager.discover()

    assert plugins == []
    assert manager.count() == 0
