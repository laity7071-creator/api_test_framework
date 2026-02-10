"""极简登录用例：纯pytest，无任何unittest"""
from core.base_request import request_util
from core.db_operation import db_util
from data.login_data import success_case
from utils.log_util import logger

def test_login_success(db_connect):
    """单个正常登录用例（仅pytest识别）"""
    logger.info(f"开始执行用例：{success_case['case_name']}")

    # 发送请求（替换为你的真实接口路径）
    resp = request_util.post(url="/syslogin/admin/user/login", json=success_case["request_data"])

    resp_json = resp.json()
    # 完善断言（覆盖核心字段）
    assert resp.status_code == success_case[
        "expected_code"], f"状态码错误：预期{success_case['expected_code']}，实际{resp.status_code}"
    assert resp_json["code"] == 200, f"业务码错误：预期200，实际{resp_json['code']}"
    assert resp_json["msg"] == "success", f"提示语错误：预期success，实际{resp_json['msg']}"
    assert "token" in resp_json["data"], "返回数据无token（登录失败）"
    assert len(resp_json["data"]["token"]) > 0, "token为空（无效登录）"

    logger.info("用例执行成功")