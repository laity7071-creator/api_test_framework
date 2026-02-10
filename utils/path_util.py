"""路径工具类：获取项目根目录、配置文件路径（完整版）"""
import os

def get_project_root():
    """
    自动识别项目根目录（找到包含config文件夹的最外层目录）
    :return: 项目根目录绝对路径
    """
    # 当前文件（path_util.py）的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 向上遍历，直到找到包含config文件夹的目录
    while True:
        # 检查当前目录下是否有config文件夹
        if os.path.exists(os.path.join(current_dir, "config")):
            return current_dir
        # 向上找父目录
        parent_dir = os.path.dirname(current_dir)
        # 到达根目录仍未找到，抛异常
        if parent_dir == current_dir:
            raise FileNotFoundError("未找到项目根目录（未发现config文件夹）")
        current_dir = parent_dir

# 全局路径常量（项目启动时自动初始化）
PROJECT_ROOT = get_project_root()
# 配置文件路径（config/config.ini）
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config", "config.ini")
# 日志目录路径（logs/）
LOG_PATH = os.path.join(PROJECT_ROOT, "logs")
# 测试报告目录路径（reports/）
REPORT_PATH = os.path.join(PROJECT_ROOT, "reports")

# 确保日志/报告目录存在（不存在则创建）
for dir_path in [LOG_PATH, REPORT_PATH]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)