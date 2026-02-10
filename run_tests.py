import os
import time
import pytest
import subprocess
import shutil  # 用于递归删除目录

# ====================== 手动配置区（按需修改） ======================
# 1. Allure.bat绝对路径（必填）
ALLURE_BAT_PATH = r"D:\LaityTest\allure-2.36.0\bin\allure.bat"
# 2. 是否生成pytest-html报告（True/False）
GENERATE_HTML_REPORT = True
# 3. 是否清空allure_report根目录（True=清空所有旧文件；False=不清空）
CLEAR_ROOT_DIR = False  # 核心：改为True即可清空根目录
# 4. 自定义HTML报告名称
CUSTOM_HTML_REPORT_NAME = "算力模块测试报告"
# ===================================================================

# 生成统一时间戳
TIMESTAMP = time.strftime("%Y%m%d_%H%M%S")

# 定义基础路径（保留你的路径设置）
REPORT_PATH = "./reports/allure_report"
# 带时间戳的Allure路径
ALLURE_RESULTS_PATH = os.path.join(REPORT_PATH, f"allure_results_{TIMESTAMP}")
ALLURE_REPORT_PATH = os.path.join(REPORT_PATH, f"allure_report_{TIMESTAMP}")

# ====================== 核心修改：清空allure_report根目录 ======================
if CLEAR_ROOT_DIR:
    if os.path.exists(REPORT_PATH):
        # 递归删除根目录下所有文件/子目录（彻底清空）
        shutil.rmtree(REPORT_PATH)
        print(f"🗑️  已清空根目录：{REPORT_PATH}")
    # 重新创建空的根目录
    os.makedirs(REPORT_PATH)
    print(f"✅ 重新创建根目录：{REPORT_PATH}")
else:
    # 不清空根目录，仅确保目录存在
    if not os.path.exists(REPORT_PATH):
        os.makedirs(REPORT_PATH)
        print(f"✅ 创建基础报告目录：{REPORT_PATH}")

if __name__ == "__main__":
    # ---------------------- 步骤1：生成pytest-html报告 ----------------------
    html_report_file = ""
    if GENERATE_HTML_REPORT:
        # 自定义报告名称 + 时间戳
        html_report_file = os.path.join(REPORT_PATH, f"{CUSTOM_HTML_REPORT_NAME}_{TIMESTAMP}.html")
        pytest_args = [
            # 指定具体用例函数
            "test_cases/SkyHash_suanli/test_login.py::test_login_success",
            "test_cases/SkyHash_suanli/test_calc_node.py::test_get_calc_node_list",
            "-v",
            f"--html={html_report_file}",
            "--self-contained-html",
            "--alluredir", ALLURE_RESULTS_PATH,
            # "--clean-alluredir"
        ]
        pytest.main(pytest_args)
        print(f"\n🎉 pytest-html报告生成完成：{html_report_file}")
    else:
        print("\nℹ️  未生成pytest-html报告（GENERATE_HTML_REPORT=False）")

    # ---------------------- 步骤2：生成Allure报告 ----------------------
    if not os.path.exists(ALLURE_BAT_PATH):
        print(f"\n❌ 错误：allure.bat不存在！路径：{ALLURE_BAT_PATH}")
    else:
        allure_cmd = [
            ALLURE_BAT_PATH,
            "generate",
            ALLURE_RESULTS_PATH,
            "-o", ALLURE_REPORT_PATH,
            # --clean 已无意义（根目录已清空，新目录为空），建议注释
            # "--clean"
        ]
        result = subprocess.run(
            allure_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8"
        )
        if result.stdout:
            print(f"\nAllure执行日志：{result.stdout}")
        if result.stderr:
            print(f"\nAllure警告/错误：{result.stderr}")
        # 提示报告路径
        allure_index_path = os.path.join(ALLURE_REPORT_PATH, "index.html")
        print(f"\n🎉 Allure报告生成完成：")
        print(f"   - Allure原始数据目录：{ALLURE_RESULTS_PATH}")
        print(f"   - Allure HTML报告路径：{allure_index_path}")

    # ---------------------- 汇总报告路径 ----------------------
    print("\n📋 本次生成的所有报告汇总：")
    if GENERATE_HTML_REPORT:
        print(f"   • pytest-html报告：{html_report_file}")
    print(f"   • Allure原始数据：{ALLURE_RESULTS_PATH}")
    print(f"   • Allure HTML报告：{allure_index_path}")