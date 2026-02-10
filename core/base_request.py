# -*- coding: utf-8 -*-
"""
【接口请求底层核心封装】
文件作用：
1. 作为项目所有接口请求的底层入口，统一封装 GET/POST/PUT/DELETE/PATCH 等请求方法
2. 封装公共逻辑：多环境切换、请求头管理、超时控制、重试机制、日志记录、异常统一处理
3. 设计原则：单一职责（仅处理请求）、高复用（所有接口复用）、易扩展（新增请求方法仅需新增函数）
4. 依赖说明：
   - requests：底层请求库
   - utils.common_util：配置读取、重试装饰器
   - utils.log_util：日志记录
"""
import requests
from requests.exceptions import (
    RequestException, Timeout, ConnectionError, HTTPError
)
# 导入项目通用工具：配置读取、重试装饰器
from utils.common_util import get_env_base_url, retry
# 导入日志工具：统一日志格式
from utils.log_util import logger


class BaseRequest:
    """
    接口请求核心类（所有接口请求的父类）
    设计思路：
    - 初始化时完成基础配置（多环境、请求头、超时），避免重复代码
    - 封装通用 _request 方法，抽离所有请求的公共逻辑（日志、重试、异常）
    - 具体请求方法（get/post等）仅需传递专属参数，调用通用方法即可
    """

    def __init__(self, env: str = "test", timeout: int = 10, retry_config: dict = None):
        """
        初始化请求配置（底层核心配置，一次初始化全局复用）
        :param env: 运行环境，可选值：test(测试)/pre(预发)/prod(生产)，默认test
        :param timeout: 请求超时时间（秒），默认10秒（避免请求挂起）
        :param retry_config: 重试配置字典，格式：{"max_retries": 3, "delay": 1}
                             max_retries：最大重试次数，delay：重试间隔（秒）
        """
        # 1. 多环境基础URL（从配置文件读取对应环境的base_url）
        self.base_url = get_env_base_url(env)
        # 2. 默认请求头（所有请求的公共头，可通过update_headers方法动态更新）
        self.headers = {
            "Content-Type": "application/json; charset=utf-8",  # 默认JSON格式
            "User-Agent": "ApiTestFramework/1.0"  # 标识请求来源
        }
        # 3. 请求超时时间（防止请求无限等待）
        self.timeout = timeout
        # 4. 重试配置（默认3次重试，间隔1秒）
        self.retry_config = retry_config or {"max_retries": 3, "delay": 1}

    def update_headers(self, headers: dict) -> None:
        """
        动态更新请求头（适配不同接口的专属头，如token、Cookie）
        :param headers: 要新增/覆盖的请求头字典，例：{"Authorization": "Bearer xxx"}
        :return: None
        """
        if not isinstance(headers, dict):
            logger.error(f"更新请求头失败：参数不是字典类型，传入值：{headers}")
            raise TypeError("headers必须是字典类型")
        self.headers.update(headers)
        logger.info(f"请求头更新完成，当前请求头：{self.headers}")

    def _get_full_url(self, path: str) -> str:
        """
        拼接完整请求URL（内部辅助方法，避免重复拼接逻辑）
        :param path: 接口路径（如：/syslogin/admin/user/login）
        :return: 完整URL（如：http://10.68.3.106:28397/syslogin/admin/user/login）
        """
        # 处理路径开头的/，避免拼接出//（如base_url末尾有/时）
        if path.startswith("/"):
            full_url = f"{self.base_url}{path}"
        else:
            full_url = f"{self.base_url}/{path}"
        logger.info(f"拼接完整URL：{full_url}")
        return full_url

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        """
        通用请求方法（核心封装，所有具体请求方法都调用此方法）
        封装逻辑：URL拼接 + 日志记录 + 重试 + 异常捕获 + 响应返回
        :param method: 请求方法（GET/POST/PUT/DELETE/PATCH，大小写均可）
        :param path: 接口路径
        :param kwargs: 可变参数，支持requests的所有参数：
                       - params: GET请求参数（字典）
                       - json: POST/PUT请求的JSON参数（字典）
                       - data: 表单请求参数（字典/字节）
                       - files: 文件上传参数（字典）
                       - cookies: Cookie参数（字典）
        :return: requests.Response对象（包含响应状态码、响应体、响应头等）
        :raises RequestException: 所有请求异常统一抛出，上层可捕获处理
        """
        # 1. 预处理：统一请求方法为大写，拼接完整URL
        method = method.upper()
        full_url = self._get_full_url(path)

        # 2. 日志记录：请求开始（便于排查问题）
        logger.info(f"===== 开始{method}请求 =====")
        logger.info(f"请求URL：{full_url}")
        logger.info(f"请求头：{self.headers}")
        # 按参数类型记录请求参数（区分GET/POST参数）
        if "params" in kwargs:
            logger.info(f"GET请求参数：{kwargs['params']}")
        if "json" in kwargs:
            logger.info(f"JSON请求参数：{kwargs['json']}")
        if "data" in kwargs:
            logger.info(f"表单请求参数：{kwargs['data']}")

        try:
            # 3. 执行请求（带重试机制）
            # 应用重试装饰器：根据初始化的重试配置设置重试次数和间隔
            @retry(
                max_retries=self.retry_config["max_retries"],
                delay=self.retry_config["delay"],
                exceptions=(Timeout, ConnectionError)  # 仅对超时/连接错误重试
            )
            def send_request():
                """内部函数：用于应用重试装饰器"""
                return requests.request(
                    method=method,
                    url=full_url,
                    headers=self.headers,
                    timeout=self.timeout,
                    **kwargs
                )

            # 执行请求（触发重试逻辑）
            response = send_request()

            # 4. 日志记录：响应结果
            logger.info(f"===== {method}请求响应 =====")
            logger.info(f"响应状态码：{response.status_code}")
            logger.info(f"响应头：{dict(response.headers)}")
            # 尝试解析响应体（避免非JSON响应报错）
            try:
                logger.info(f"响应体（JSON）：{response.json()}")
            except ValueError:
                logger.info(f"响应体（文本）：{response.text}")

            # 5. 主动抛出HTTP错误（状态码>=400时，便于上层捕获）
            response.raise_for_status()

            return response

        except (Timeout, ConnectionError) as e:
            # 超时/连接错误（已重试，仍失败则记录并抛出）
            logger.error(f"{method}请求失败：{full_url}，超时/连接错误，错误信息：{str(e)}")
            raise RequestException(f"请求超时/连接失败：{str(e)}") from e
        except HTTPError as e:
            # HTTP错误（状态码>=400）
            logger.error(f"{method}请求失败：{full_url}，HTTP错误，状态码：{response.status_code}，错误信息：{str(e)}")
            raise RequestException(f"HTTP请求失败：状态码{response.status_code}，{str(e)}") from e
        except RequestException as e:
            # 其他请求错误（如URL无效、参数错误）
            logger.error(f"{method}请求失败：{full_url}，通用请求错误，错误信息：{str(e)}")
            raise RequestException(f"请求失败：{str(e)}") from e
        except Exception as e:
            # 未知错误（兜底捕获）
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