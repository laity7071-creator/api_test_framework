"""接口请求封装：适配多环境，解决NoSectionError"""
import requests
from utils.common_util import read_config, get_env_base_url, retry  # 新增get_env_base_url
from utils.log_util import logger

class BaseRequest:
    def __init__(self, env="test"):  # 默认使用测试环境
        # 关键修改：改用多环境函数，不再读[ENV]段
        self.base_url = get_env_base_url(env)
        self.headers = {"Content-Type": "application/json"}

    @retry(max_retries=3, delay=1)
    def post(self, url, json=None, headers=None):
        full_url = f"{self.base_url}{url}"
        # 合并自定义headers（如token）
        if headers:
            self.headers.update(headers)
        try:
            logger.info(f"POST请求：{full_url}，参数：{json}，头信息：{self.headers}")
            resp = requests.post(full_url, json=json, headers=self.headers, timeout=10)
            logger.info(f"响应：{resp.status_code}，{resp.text}")
            return resp
        except Exception as e:
            logger.error(f"POST请求失败：{str(e)}")
            raise

# 初始化请求对象（默认用测试环境）
request_util = BaseRequest(env="test")