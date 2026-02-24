import os
import shutil
import yaml
from pathlib import Path

def copy_config_path_if_not_exists(config_path: str):
    """
    如果目标路径不存在，则从源路径复制配置文件夹
    """
    config_path = Path(config_path)
    if not config_path.exists():
        # 如果不存在，则创建，并把配置复制到当前目录
        src_config_path = Path(__file__).parent / "config"
        shutil.copytree(src_config_path, config_path)
        print("✅ 默认配置文件已创建，路径：", config_path)

def load_or_create_config(config_path: str = "agent_discovery_config") -> dict:
    """
    加载配置文件，如果不存在则创建一个默认配置文件。
    """
    copy_config_path_if_not_exists(config_path)
    config_yaml_path = Path(config_path) / "config.yaml"

    with open(config_yaml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_or_create_prompt(config_path: str = "agent_discovery_config") -> dict:
    """
    加载摘要提示词配置
    """
    copy_config_path_if_not_exists(config_path)
    summary_prompt_path = Path(config_path) / "prompt_summary.md"


    prompts=dict()
    with open(summary_prompt_path, "r", encoding="utf-8") as f:
        prompts["summary"] = f.read()
    return prompts