"""通用工具类：配置读取、加密、重试、多环境切换（完整版）"""
import os
import configparser
import hashlib
import time
import functools
import requests  # 提前导入，解决retry装饰器依赖
from utils.path_util import CONFIG_PATH, PROJECT_ROOT

# -------------------------- 核心：配置读取函数（解决"找不到read_config"） --------------------------
# 全局配置缓存（读取一次，避免重复解析config.ini）
_config_cache = None


def read_config(section, option):
    """
    读取配置文件（优先级：环境变量 > 配置文件）
    :param section: 配置段（如ENV_TEST、DATABASE）
    :param option: 配置项（如base_url、host）
    :return: 配置值（自动清理行内注释、替换路径占位符）
    """
    global _config_cache
    # 1. 初始化配置缓存（仅第一次调用时解析config.ini）
    if _config_cache is None:
        _config_cache = configparser.ConfigParser()
        # 确保配置文件存在，避免读取失败
        if not os.path.exists(CONFIG_PATH):
            raise FileNotFoundError(f"配置文件不存在：{CONFIG_PATH}")
        _config_cache.read(CONFIG_PATH, encoding="utf-8")

    # 2. 优先读取环境变量（格式：SECTION_OPTION，如ENV_TEST_BASE_URL）
    env_key = f"{section.upper()}_{option.upper()}"
    if env_key in os.environ:
        return os.environ[env_key]

    # 3. 读取配置文件（处理行内注释、路径占位符）
    try:
        value = _config_cache.get(section, option)
    except configparser.NoSectionError:
        raise ValueError(f"配置文件中无此段：{section}")
    except configparser.NoOptionError:
        raise ValueError(f"配置段[{section}]中无此配置项：{option}")

    # 清理行内注释（如 "10485760 # 10MB" → "10485760"）
    if '#' in value:
        value = value.split('#')[0].strip()
    # 替换项目根目录占位符（${PROJECT_ROOT} → 实际路径）
    if "${PROJECT_ROOT}" in value:
        value = value.replace("${PROJECT_ROOT}", PROJECT_ROOT)

    return value


# -------------------------- 多环境配置函数（解决"找不到get_env_base_url"） --------------------------
def get_env_base_url(env="test"):
    """
    根据环境获取接口基础URL
    :param env: 环境标识（test=测试/ pre=预发/ prod=生产）
    :return: 对应环境的base_url
    """
    # 拼接环境配置段（如 env=test → ENV_TEST）
    env_section = f"ENV_{env.upper()}"
    # 调用上面的read_config函数读取对应环境的base_url
    return read_config(env_section, "base_url_SkyHash_suanli")


# -------------------------- 基础工具函数（保留之前的核心功能） --------------------------
def md5_encrypt(data):
    """MD5加密（返回32位小写结果）"""
    if not isinstance(data, str):
        data = str(data)
    md5 = hashlib.md5()
    md5.update(data.encode("utf-8"))
    return md5.hexdigest()


def get_timestamp():
    """获取秒级时间戳（整数）"""
    return int(time.time())


def retry(max_retries=3, delay=1, exceptions=(requests.exceptions.Timeout, requests.exceptions.ConnectionError)):
    """
    接口重试装饰器（默认重试3次，间隔1秒，仅捕获超时/连接错误）
    :param max_retries: 最大重试次数
    :param delay: 重试间隔（秒）
    :param exceptions: 触发重试的异常类型
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    # 这里暂用print，若需日志可导入logger（确保无循环导入）
                    print(f"请求失败，重试{retries}/{max_retries}：{str(e)}")
                    time.sleep(delay)
            raise Exception(f"重试{max_retries}次后仍失败")

        return wrapper

    return decorator