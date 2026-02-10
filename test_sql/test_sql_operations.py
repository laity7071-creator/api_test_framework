"""SQL测试用例（仅写用例逻辑，核心逻辑在core/db_operation.py）"""
import pytest
from utils.log_util import logger
from core.db_operation import db_util

# 测试表名（建议用临时表）
TEST_TABLE = "test_user_temp"

# -------------------------- 前置/后置（仅用例内的辅助Fixture） --------------------------
@pytest.fixture(scope="module", autouse=True)
def prepare_test_table(db_connect):
    """模块级：创建/删除测试表（仅用例内使用，不污染全局夹具）"""
    # 创建表
    create_sql = f"""
    CREATE TABLE IF NOT EXISTS {TEST_TABLE} (
        id INT PRIMARY KEY AUTO_INCREMENT,
        username VARCHAR(50) NOT NULL UNIQUE,
        age INT,
        email VARCHAR(100)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    db_util.execute(create_sql)
    logger.info(f"测试表[{TEST_TABLE}]创建成功")

    yield

    # 删除表
    drop_sql = f"DROP TABLE IF EXISTS {TEST_TABLE};"
    db_util.execute(drop_sql)
    logger.info(f"测试表[{TEST_TABLE}]已删除")

# -------------------------- SQL用例 --------------------------
def test_sql_insert_single(db_connect):
    """测试单条插入"""
    insert_sql = f"INSERT INTO {TEST_TABLE} (username, age, email) VALUES ('test_01', 25, 'test01@example.com');"
    rows = db_util.execute(insert_sql)
    assert rows == 1, "单条插入失败"

    # 验证
    check_sql = f"SELECT * FROM {TEST_TABLE} WHERE username = 'test_01'"
    result = db_util.query_one(check_sql)
    assert result["username"] == "test_01", "插入数据验证失败"

def test_sql_query_multi(db_connect):
    """测试多条查询"""
    # 先批量插入
    batch_data = [("test_02", 26, "test02@example.com"), ("test_03", 27, "test03@example.com")]
    batch_sql = f"INSERT INTO {TEST_TABLE} (username, age, email) VALUES (%s, %s, %s);"
    db_util.executemany(batch_sql, batch_data)

    # 查询
    query_sql = f"SELECT * FROM {TEST_TABLE} WHERE age > 25"
    result = db_util.query_all(query_sql)
    assert len(result) >= 2, "多条查询失败"

def test_sql_transaction_rollback(db_connect):
    """测试事务回滚"""
    db_util.begin_transaction()
    try:
        # 插入重复数据触发异常
        db_util.execute(f"INSERT INTO {TEST_TABLE} (username, age, email) VALUES ('test_01', 25, 'test01@example.com');")
        db_util.commit()
    except Exception as e:
        db_util.rollback()
        # 验证回滚
        check_sql = f"SELECT COUNT(*) AS total FROM {TEST_TABLE} WHERE username = 'test_01'"
        result = db_util.query_one(check_sql)
        assert result["total"] == 1, "事务回滚失败"
        logger.info(f"事务回滚测试通过：{e}")

if __name__ == "__main__":
    pytest.main()