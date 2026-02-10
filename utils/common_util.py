"""通用工具类（仅封装配置读取/加密/重试，无任何用例代码）"""
import os
import configparser
import hashlib
import time
import functools
import requests
from utils.path_util import CONFIG_PATH, PROJECT_ROOT

# 配置缓存（避免重复解析）
_config_cache = None

# -------------------------- 核心配置读取 --------------------------
def read_config(section, option):
    """读取配置（环境变量 > 配置文件，自动清理注释/替换路径）"""
    global _config_cache
    if _config_cache is None:
        _config_cache = configparser.ConfigParser()
        if not os.path.exists(CONFIG_PATH):
            raise FileNotFoundError(f"配置文件不存在：{CONFIG_PATH}")
        _config_cache.read(CONFIG_PATH, encoding="utf-8")

    # 优先读环境变量
    env_key = f"{section.upper()}_{option.upper()}"
    if env_key in os.environ:
        return os.environ[env_key]

    # 读配置文件
    try:
        value = _config_cache.get(section, option)
    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        raise ValueError(f"配置读取失败：{e}")

    # 清理注释/替换路径占位符
    if '#' in value:
        value = value.split('#')[0].strip()
    if "${PROJECT_ROOT}" in value:
        value = value.replace("${PROJECT_ROOT}", PROJECT_ROOT)
    return value

# -------------------------- 多环境URL --------------------------
def get_env_base_url(env="test"):
    """获取指定环境的接口基础URL"""
    env_section = f"ENV_{env.upper()}"
    return read_config(env_section, "base_url_SkyHash_suanli")

# -------------------------- SSH配置读取 --------------------------
def get_ssh_config(option, env="test"):
    """读取指定环境的单个SSH配置项"""
    env_section = f"ENV_{env.upper()}"
    return read_config(env_section, option)

def get_ssh_config_batch(env="test"):
    """批量读取指定环境的所有SSH配置（自动转端口为整数）"""
    keys = ["ssh_host", "ssh_port", "ssh_user", "ssh_password"]
    config = {k: get_ssh_config(k, env) for k in keys}
    config["ssh_port"] = int(config["ssh_port"])
    return config

# -------------------------- 基础工具 --------------------------
def md5_encrypt(data):
    """MD5加密（返回32位小写）"""
    if not isinstance(data, str):
        data = str(data)
    md5 = hashlib.md5()
    md5.update(data.encode("utf-8"))
    return md5.hexdigest()

def get_timestamp():
    """获取秒级时间戳（整数）"""
    return int(time.time())

def retry(max_retries=3, delay=1, exceptions=(requests.exceptions.Timeout, requests.exceptions.ConnectionError)):
    """接口重试装饰器（仅捕获指定异常）"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    print(f"重试{retries}/{max_retries}：{e}")
                    time.sleep(delay)
            raise Exception(f"重试{max_retries}次后仍失败")
        return wrapper
    return decorator