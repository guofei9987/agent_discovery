import os
import shutil
import yaml
from pathlib import Path


def load_or_create_config(config_path: str = "agent_discovery_config") -> dict:
    """
    加载配置文件，如果不存在则创建一个默认配置文件。
    """
    config_yaml_filename = "config.yaml"
    config_path = Path(config_path)
    if not config_path.exists():
        # 如果不存在，则创建，并把配置复制到当前目录
        src_config_path = Path(__file__).parent / "config"
        shutil.copytree(src_config_path, config_path)
        print("✅ 默认配置文件已创建，路径：", config_path)

    config_yaml_path = config_path / config_yaml_filename

    if not config_yaml_path.exists():
        raise FileNotFoundError(f"配置文件不存在，路径：{config_yaml_path}")

    with open(config_yaml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
