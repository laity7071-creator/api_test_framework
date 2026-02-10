"""日志工具类：带颜色输出，解决全红问题"""
import os
import logging
import time
from logging.handlers import RotatingFileHandler
from utils.path_util import LOG_PATH
from utils.common_util import read_config

# -------------------------- 日志颜色配置 --------------------------
# ANSI颜色码（Windows/Linux/Mac通用）
COLOR_CODES = {
    logging.DEBUG: '\033[94m',    # 蓝色
    logging.INFO: '\033[92m',     # 绿色
    logging.WARNING: '\033[93m',  # 黄色
    logging.ERROR: '\033[91m',    # 红色
    logging.CRITICAL: '\033[95m'  # 紫色
}
RESET_CODE = '\033[0m'  # 重置颜色

class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式器"""
    def format(self, record):
        # 给不同级别日志添加颜色前缀
        color_code = COLOR_CODES.get(record.levelno, '')
        # 格式化日志内容（保留原有格式+颜色）
        log_message = super().format(record)
        # 返回带颜色的日志（仅控制台输出用，文件输出不带颜色）
        return f"{color_code}{log_message}{RESET_CODE}"

# -------------------------- 初始化日志 --------------------------
def init_logger():
    # 1. 读取日志配置
    LOG_LEVEL = read_config("LOG", "log_level")
    LOG_MAX_BYTES = int(read_config("LOG", "log_max_bytes"))
    LOG_BACKUP_COUNT = int(read_config("LOG", "log_backup_count"))

    # 2. 创建logger
    logger = logging.getLogger("api_test")
    logger.setLevel(getattr(logging, LOG_LEVEL))
    logger.propagate = False  # 防止日志重复输出

    # 3. 文件处理器（无颜色，纯文本）
    log_file = os.path.join(LOG_PATH, f"api_test_{time.strftime('%Y%m%d')}.log")
    file_handler = RotatingFileHandler(
        log_file, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT, encoding="utf-8"
    )
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)

    # 4. 控制台处理器（带颜色）
    console_handler = logging.StreamHandler()
    colored_formatter = ColoredFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(colored_formatter)

    # 5. 添加处理器
    if not logger.handlers:  # 避免重复添加
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

# 全局日志对象
logger = init_logger()