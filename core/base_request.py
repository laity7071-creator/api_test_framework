# -*- coding: utf-8 -*-
"""改造后：自动携带全局token的请求封装"""
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError, HTTPError
from utils.common_util import get_env_base_url, retry
from utils.log_util import logger
# 新增：导入token管理器
from core.token_manager import token_manager


class BaseRequest:
    def __init__(self, env: str = "test", timeout: int = 10, retry_config: dict = None):
        self.base_url = get_env_base_url(env)
        self.headers = {
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "ApiTestFramework/1.0"
        }
        self.timeout = timeout
        self.retry_config = retry_config or {"max_retries": 3, "delay": 1}

    def update_headers(self, headers: dict) -> None:
        """动态更新请求头（保留原有逻辑）"""
        if not isinstance(headers, dict):
            logger.error(f"更新请求头失败：参数不是字典类型，传入值：{headers}")
            raise TypeError("headers必须是字典类型")
        self.headers.update(headers)
        logger.info(f"请求头更新完成，当前请求头：{self.headers}")

    def _add_token_to_headers(self):
        """新增：自动将全局token加入请求头（核心逻辑）"""
        if token_manager.is_token_valid():
            # 假设token放在Authorization头（格式：Bearer + 空格 + token，根据实际接口调整）
            self.headers["Authorization"] = f"{token_manager.get_token()}"
            logger.info("已自动将全局token加入请求头")
        else:
            logger.warning("全局token无效，请求头未添加token（若接口无需token可忽略）")

    def _get_full_url(self, path: str) -> str:
        """保留原有逻辑：拼接完整URL"""
        if path.startswith("/"):
            full_url = f"{self.base_url}{path}"
        else:
            full_url = f"{self.base_url}/{path}"
        logger.info(f"拼接完整URL：{full_url}")
        return full_url

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        """改造核心：请求前自动添加token"""
        method = method.upper()
        full_url = self._get_full_url(path)

        # 新增：请求前自动添加token到请求头
        self._add_token_to_headers()

        logger.info(f"===== 开始{method}请求 =====")
        logger.info(f"请求URL：{full_url}")
        logger.info(f"请求头：{self.headers}")
        if "params" in kwargs:
            logger.info(f"GET请求参数：{kwargs['params']}")
        if "json" in kwargs:
            logger.info(f"JSON请求参数：{kwargs['json']}")

        try:
            @retry(
                max_retries=self.retry_config["max_retries"],
                delay=self.retry_config["delay"],
                exceptions=(Timeout, ConnectionError)
            )
            def send_request():
                return requests.request(
                    method=method,
                    url=full_url,
                    headers=self.headers,
                    timeout=self.timeout, **kwargs
                )

            response = send_request()
            logger.info(f"===== {method}请求响应 =====")
            logger.info(f"响应状态码：{response.status_code}")
            try:
                logger.info(f"响应体（JSON）：{response.json()}")
            except ValueError:
                logger.info(f"响应体（文本）：{response.text}")
            response.raise_for_status()
            return response

        except (Timeout, ConnectionError) as e:
            logger.error(f"{method}请求失败：{full_url}，超时/连接错误，错误信息：{str(e)}")
            raise RequestException(f"请求超时/连接失败：{str(e)}") from e
        except HTTPError as e:
            logger.error(f"{method}请求失败：{full_url}，HTTP错误，状态码：{response.status_code}，错误信息：{str(e)}")
            raise RequestException(f"HTTP请求失败：状态码{response.status_code}，{str(e)}") from e
        except RequestException as e:
            logger.error(f"{method}请求失败：{full_url}，通用请求错误，错误信息：{str(e)}")
            raise RequestException(f"请求失败：{str(e)}") from e
        except Exception as e:
            logger.error(f"{method}请求失败：{full_url}，未知错误，错误信息：{str(e)}")
            raise Exception(f"未知请求错误：{str(e)}") from e

    def get(self, path: str, params: dict = None, **kwargs) -> requests.Response:
        """
        GET请求方法（查询数据专用，参数拼在URL后）
        :param path: 接口路径，例：/sys/user/info
        :param params: GET请求参数，字典类型，例：{"userId": 113}
        :param kwargs: 其他可选参数（如cookies、headers等）
        :return: requests.Response对象
        """
        # 调用通用_request方法，指定GET方法，传递params参数
        return self._request(method="GET", path=path, params=params, **kwargs)

    def post(self, path: str, json: dict = None, data: dict = None, files: dict = None, **kwargs) -> requests.Response:
        """
        POST请求方法（创建/提交数据专用，支持JSON/表单/文件上传）
        :param path: 接口路径，例：/syslogin/admin/user/login
        :param json: JSON格式请求体（优先使用），例：{"account": "laity.wang", "password": "xxx"}
        :param data: 表单格式请求体（如application/x-www-form-urlencoded），例：{"username": "test"}
        :param files: 文件上传参数，例：{"file": open("test.png", "rb")}
        :param kwargs: 其他可选参数（如cookies、headers等）
        :return: requests.Response对象
        """
        # 调用通用_request方法，指定POST方法，传递json/data/files参数
        return self._request(method="POST", path=path, json=json, data=data, files=files, **kwargs)

    def put(self, path: str, json: dict = None, **kwargs) -> requests.Response:
        """
        PUT请求方法（更新数据专用，全量更新）
        :param path: 接口路径，例：/sys/user/update
        :param json: 更新的JSON数据，例：{"userId": 113, "username": "new_name"}
        :param kwargs: 其他可选参数（如cookies、headers等）
        :return: requests.Response对象
        """
        return self._request(method="PUT", path=path, json=json, **kwargs)

    def delete(self, path: str, params: dict = None, **kwargs) -> requests.Response:
        """
        DELETE请求方法（删除数据专用）
        :param path: 接口路径，例：/sys/user/delete
        :param params: 删除参数，例：{"userId": 113}
        :param kwargs: 其他可选参数（如cookies、headers等）
        :return: requests.Response对象
        """
        return self._request(method="DELETE", path=path, params=params, **kwargs)

    def patch(self, path: str, json: dict = None, **kwargs) -> requests.Response:
        """
        PATCH请求方法（更新数据专用，增量更新）
        :param path: 接口路径，例：/sys/user/patch
        :param json: 增量更新的JSON数据，例：{"username": "new_name"}
        :param kwargs: 其他可选参数（如cookies、headers等）
        :return: requests.Response对象
        """
        return self._request(method="PATCH", path=path, json=json, **kwargs)


# -------------------------- 全局请求对象（项目通用） --------------------------
"""
全局请求对象说明：
1. 初始化时指定默认环境为test（测试环境），超时10秒，重试3次
2. 项目中所有接口可直接导入此对象使用，无需重复初始化
3. 如需切换环境，可重新初始化：request_util = BaseRequest(env="pre")
"""
request_util = BaseRequest(
    env="test",
    timeout=10,
    retry_config={"max_retries": 3, "delay": 1}
)