# -*- coding: utf-8 -*-
"""
登录接口测试用例
依赖说明：
1. core.base_request.request_util：全局接口请求实例（已初始化，直接调用）
2. data.login_data.success_case：登录成功测试数据
3. conftest.db_connect：数据库连接夹具（可选，若无需数据库可删除）
"""
import pytest

from utils.log_util import logger
# 关键修改：导入全局实例request_util，而非BaseRequest类
from core.base_request import request_util
from core.db_operation import db_util  # 导入数据库操作实例
from data.login_data import success_case


def test_login_success(db_connect):
    """
    正常登录用例（账号密码正确）
    测试步骤：
    1. 读取登录成功测试数据
    2. 调用登录接口（POST请求）
    3. 断言响应结果（状态码、业务码、提示语、token）
    4. （可选）数据库验证（当前仅做连接/关闭，无实际校验）
    """
    # 1. 日志记录：用例开始
    logger.info(f"开始执行用例：{success_case['case_name']}")
    # 执行SELECT 1（最简单的数据库连通性校验）
    sql = "SELECT 1 as result;"
    sql_result = db_util.query(sql)
    logger.info(f"sql的查询在这里{sql_result}")
    # 正确写法（规范）
    logger.info("sql的查询在这里：%s", sql_result)

    try:
        # 2. 调用登录接口（关键修改：用request_util实例调用post方法，而非BaseRequest类）
        resp = request_util.post(
            path="/cdpapi/v1/cdp/admin/user/login",  # 接口路径（base_url已在request_util中初始化）
            json=success_case["request_data_SkyHash_suanli"]   # 请求参数（JSON格式）
        )


        # 3. 解析响应体（JSON格式）
        resp_json = resp.json()

        # 4. 断言（核心校验，确保登录成功）
        # 4.1 断言HTTP状态码
        assert resp.status_code == success_case["expected_code"], \
            f"HTTP状态码错误：预期{success_case['expected_code']}，实际{resp.status_code}"
        # 4.2 断言业务码（接口自定义的code）
        assert resp_json["ret"]["code"] == 0, f"业务码错误：预期0，实际{resp_json['code']}"
        # 4.3 断言提示语
        assert resp_json["ret"]["msg"] == success_case["expected_msg"], \
            f"提示语错误：预期{success_case['expected_msg']}，实际{resp_json['msg']}"
        # 4.4 断言token存在且非空（登录成功的核心标识）
        assert "token" in resp_json["body"], "响应数据中无token，登录失败"
        assert len(resp_json["body"]["token"]) > 0, "token为空，登录失败"

        # 5. 日志记录：用例成功
        logger.info("用例执行成功")

    except Exception as e:
        # 异常捕获：记录错误日志，重新抛出异常（让pytest标记用例失败）
        logger.error(f"用例执行失败：{str(e)}", exc_info=True)
        raise  # 必须重新抛出，否则pytest会认为用例成功

if __name__ == "__main__":
    # 场景1：执行单个函数（直接调用，适合快速调试）
    print("===== 执行 test_login_success =====")
    test_login_success()  # 直接调用函数，无需启动pytest

    # 场景2：执行单个函数（通过pytest执行，保留pytest的断言/日志格式，更规范）
    print("\n===== 通过pytest执行 test_login_success =====")
    pytest.main([__file__, "::test_login_success", "-v", "-s"])  # -v显示详情，-s输出日志

    # 场景3：执行多个函数（用逗号分隔）
    # pytest.main([__file__, "::test_login_success", "::test_login_password_error", "-v", "-s"])