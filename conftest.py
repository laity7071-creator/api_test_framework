"""全局pytest夹具（仅管理资源生命周期，无任何用例代码）"""
import pytest
from core.db_operation import db_util
from core.ssh_operation import SSHOperation
from utils.log_util import logger

# -------------------------- 数据库夹具（修改scope为module） --------------------------
@pytest.fixture(scope="module")  # 关键修改：从function改为module
def db_connect():
    """模块级：数据库连接（整个测试文件只连接/关闭一次）"""
    db_util.connect()
    yield  # 无返回值，测试用例直接调用db_util
    db_util.close()

# -------------------------- SSH夹具（保持不变） --------------------------
@pytest.fixture(scope="function")
def ssh_obj(request):
    """函数级：SSH连接（自动创建/关闭，支持指定环境）"""
    # 从用例标记获取环境，默认test
    env = request.node.get_closest_marker("ssh_env").args[0] if request.node.get_closest_marker("ssh_env") else "test"
    # 跳过标记
    if request.node.get_closest_marker("skip_ssh"):
        pytest.skip("标记跳过SSH测试")

    # 前置：创建SSH对象
    obj = SSHOperation(env=env)
    logger.info(f"SSH夹具初始化完成（环境：{env}，主机：{obj.ssh_host}）")

    yield obj  # 返回SSH对象给用例

    # 后置：关闭连接
    obj.close()
    logger.info("SSH夹具已关闭连接")