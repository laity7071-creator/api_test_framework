from utils.common_util import md5_encrypt, get_timestamp

success_case = {
    "case_name": "正常登录-账号密码正确",
    "request_data": {
        "account": "laity.wang",
        "systemHost": "esport-diskless-v1",
        "password": "fKvOcEwY+O8ylM2CV8BHrQ==",
        "captchaId": "",
        "verifyCode": ""
    },
    "expected_code": 200,
    "expected_msg": "success"
}
