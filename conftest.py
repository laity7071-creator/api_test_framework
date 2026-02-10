"""极简pytest夹具"""
import pytest
from core.db_operation import db_util
from utils.log_util import logger

@pytest.fixture(scope="function")
def db_connect():
    db_util.connect()
    yield
    db_util.close()