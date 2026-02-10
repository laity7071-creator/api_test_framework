from utils.common_util import md5_encrypt, get_timestamp

success_case = {
    "case_name": "正常登录-账号密码正确",
    "request_path_SkyHash_suanli":"/cdpapi/v1/cdp/admin/user/login",
    "request_data_SkyHash_suanli": {

            "account": "laityadmin",
            "password": "wxNlFclzoKyK4ljtj/yLvQ==",
            "platform": 1

    },
    "expected_code": 200,
    "expected_msg": "success"
}
