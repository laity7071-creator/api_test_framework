"""SSH测试用例（适配认证/命令优化版）"""
import pytest
import os
from core.ssh_operation import SSHOperation, exec_ssh_command
from utils.log_util import logger  # 导入日志（如果有）

# ====================== 可选：测试配置（按需调整） ======================
# TEST_ENV = "test"  # 测试环境
# SKIP_SSH_TEST = False  # 若认证暂时无法解决，设为True跳过所有SSH测试
# SSH_TEST_COMMAND = "tail -n 100 /data/logs/diskless-service/diskless_service.log"  # 替换tail -f为tail -n（避免阻塞）

SSH_TEST_COMMAND = "tail -n 100 /data/logs/diskless-service/diskless_service.log"  # 替换tail -f为tail -n（避免阻塞）

# ====================== 测试用例（微调，保留原有逻辑） ======================
def test_ssh_exec_ls(ssh_obj):
    """测试执行ls命令（基础连通性测试，替换为简单命令优先验证）"""
    try:
        # 先执行简单命令（如pwd）验证连通性，再执行日志查询
        simple_cmd = "pwd"
        stdout, stderr = ssh_obj.execute_command(simple_cmd)

        # 断言：无执行错误
        assert stderr == "", f"执行[{simple_cmd}]失败：{stderr}"
        logger.info(f"简单命令[{simple_cmd}]执行成功，结果：{stdout}")

        # 执行日志查询命令（替换tail -f为tail -n，避免阻塞）
        stdout, stderr = ssh_obj.execute_command(SSH_TEST_COMMAND)
        # stdout, stderr = ssh_obj.execute_command("tail -n 100 /data/logs/diskless-service/diskless_service.log")
        assert stderr == "", f"执行日志命令失败：{stderr}"
        # 可选：断言日志非空（根据实际场景）
        # assert len(stdout) > 0, "日志查询结果为空"
        logger.info(f"日志命令执行成功，返回行数：{len(stdout.splitlines())}")
        print(f"日志最后100行：\n{stdout[:500]}")  # 仅打印前500字符，避免刷屏

    except Exception as e:
        # 友好报错，定位问题
        pytest.fail(f"SSH命令执行异常：{str(e)}")

# ====================== 本地调试（可选） ======================
if __name__ == "__main__":
    # 运行指定用例，开启详细日志
    pytest.main(["-v", __file__, "-s"])