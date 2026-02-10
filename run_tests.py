# 项目根目录新建run_tests.py
import os
import pytest
from utils.path_util import REPORT_PATH

if __name__ == "__main__":
    # 生成带样式的HTML报告
    report_file = os.path.join(REPORT_PATH, f"test_report_{time.strftime('%Y%m%d_%H%M%S')}.html")
    pytest.main([
        "test_cases/",
        "-v",
        f"--html={report_file}",
        "--self-contained-html"  # 报告包含CSS，可独立打开
    ])