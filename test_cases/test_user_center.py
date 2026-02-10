import pytest
from core.base_request import request_util
from core.db_operation import db_util
from core.ssh_operation import ssh_util
from data.user_center_data import user_center_data
from utils.log_util import logger


class TestUserCenter:
    """个人中心接口测试用例类（优化版）"""

    def test_get_user_info(self, init_db_ssh, login_token):
        """
        获取个人信息接口测试
        :param init_db_ssh: 数据库/SSH连接夹具
        :param login_token: 动态登录token夹具
        """
        case = user_center_data.get_user_info_case
        logger.info(f"开始执行用例：{case['case_name']}")

        # 1. 先通过SSH检查接口服务状态（前置条件）
        stdout, stderr = ssh_util.execute_command("ps -ef | grep api_server | grep -v grep")
        assert len(stdout) > 0, f"接口服务未运行（SSH验证失败），错误：{stderr}"

        # 2. 发送请求（使用动态token，替代硬编码）
        case["headers"]["token"] = login_token  # 替换为动态token
        response = request_util.get(
            url="/api/v1/user/info",
            params=case["request_params"],
            headers=case["headers"]
        )

        # 3. 响应结果断言
        response_json = response.json()
        assert response.status_code == case[
            "expected_code"], f"状态码断言失败，预期：{case['expected_code']}，实际：{response.status_code}"
        assert response_json["data"]["username"] == case[
            "expected_username"], f"用户名断言失败，预期：{case['expected_username']}，实际：{response_json['data']['username']}"

        # 4. 数据库验证
        sql = "SELECT nickname, phone FROM user WHERE id = %s"
        result = db_util.query(sql, (case["request_params"]["user_id"],))
        assert response_json["data"]["nickname"] == result[0]["nickname"], "昵称数据库验证失败"
        assert response_json["data"]["phone"] == result[0]["phone"], "手机号数据库验证失败"

        logger.info("获取个人信息用例执行完成")

    def test_update_user_info(self, init_db_ssh, login_token, restore_user_info):
        """
        更新个人信息接口测试（使用数据还原夹具）
        :param init_db_ssh: 数据库/SSH连接夹具
        :param login_token: 动态登录token夹具
        :param restore_user_info: 数据还原夹具
        """
        case = user_center_data.update_user_info_case
        logger.info(f"开始执行用例：{case['case_name']}")

        # 1. 发送请求（使用动态token）
        case["headers"]["token"] = login_token
        response = request_util.put(
            url="/api/v1/user/info",
            json=case["request_data"],
            headers=case["headers"]
        )

        # 2. 响应结果断言
        response_json = response.json()
        assert response.status_code == case["expected_code"], f"状态码断言失败"
        assert response_json["msg"] == case["expected_msg"], f"提示语断言失败"

        # 3. 数据库验证
        sql = "SELECT nickname FROM user WHERE id = %s"
        result = db_util.query(sql, (case["request_data"]["user_id"],))
        assert result[0]["nickname"] == case["request_data"]["nickname"], "昵称更新失败（数据库验证）"

        logger.info("更新个人信息用例执行完成")
        # 执行完后，restore_user_info夹具会自动还原数据