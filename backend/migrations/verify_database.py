"""
验证数据库创建和权限
在管理员执行完 00_admin_setup.sql 后运行此脚本
"""
import pymysql

DB_CONFIG = {
    'host': '23.19.231.78',
    'port': 3306,
    'user': 'work',
    'password': 's4TUPM.qXmfvAUu',
    'charset': 'utf8mb4'
}

def verify_database():
    """验证数据库和权限"""
    print("=" * 60)
    print("验证 textdiff 数据库配置")
    print("=" * 60)

    try:
        # 连接到 MySQL
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()

        print("\n✓ MySQL 连接成功")

        # 1. 检查数据库是否存在
        print("\n[1] 检查 textdiff 数据库...")
        cursor.execute("SHOW DATABASES LIKE 'textdiff'")
        result = cursor.fetchone()

        if result:
            print("  ✓ textdiff 数据库已存在")
        else:
            print("  ✗ textdiff 数据库不存在")
            print("  请管理员执行 00_admin_setup.sql")
            return False

        # 2. 检查用户权限
        print("\n[2] 检查用户权限...")
        cursor.execute("SHOW GRANTS FOR CURRENT_USER")
        grants = cursor.fetchall()

        has_textdiff_permission = False
        print("  当前权限:")
        for grant in grants:
            grant_str = grant[0]
            print(f"    {grant_str}")
            if 'textdiff' in grant_str.lower():
                has_textdiff_permission = True

        if has_textdiff_permission:
            print("  ✓ 已授予 textdiff 数据库权限")
        else:
            print("  ✗ 未找到 textdiff 数据库权限")
            print("  请管理员执行 GRANT 语句")
            return False

        # 3. 测试连接到 textdiff 数据库
        print("\n[3] 测试连接 textdiff 数据库...")
        cursor.execute("USE textdiff")
        print("  ✓ 成功切换到 textdiff 数据库")

        # 4. 测试创建表权限
        print("\n[4] 测试创建表权限...")
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS _test_permission (
                    id INT PRIMARY KEY,
                    name VARCHAR(50)
                )
            """)
            print("  ✓ 有创建表权限")

            # 清理测试表
            cursor.execute("DROP TABLE IF EXISTS _test_permission")
            print("  ✓ 有删除表权限")
        except pymysql.Error as e:
            print(f"  ✗ 权限测试失败: {e}")
            return False

        # 5. 检查字符集
        print("\n[5] 检查数据库字符集...")
        cursor.execute("""
            SELECT DEFAULT_CHARACTER_SET_NAME, DEFAULT_COLLATION_NAME
            FROM information_schema.SCHEMATA
            WHERE SCHEMA_NAME = 'textdiff'
        """)
        charset_info = cursor.fetchone()

        if charset_info:
            charset, collation = charset_info
            print(f"  字符集: {charset}")
            print(f"  排序规则: {collation}")

            if charset == 'utf8mb4':
                print("  ✓ 字符集配置正确")
            else:
                print(f"  ⚠ 字符集应该是 utf8mb4，当前是 {charset}")

        print("\n" + "=" * 60)
        print("✅ 所有验证通过！可以继续执行表结构初始化。")
        print("=" * 60)
        print("\n下一步：")
        print("  python migrations/init_database.py")
        print()

        cursor.close()
        connection.close()

        return True

    except pymysql.Error as e:
        print(f"\n❌ 验证失败: {e}")
        return False

if __name__ == '__main__':
    verify_database()
