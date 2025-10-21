"""测试 MySQL 连接"""
import pymysql

DB_CONFIG = {
    'host': '23.19.231.78',
    'port': 3306,
    'user': 'work',
    'password': 's4TUPM.qXmfvAUu',
    'charset': 'utf8mb4'
}

print("测试 MySQL 连接...")
print(f"主机: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
print(f"用户: {DB_CONFIG['user']}")

try:
    connection = pymysql.connect(**DB_CONFIG)
    cursor = connection.cursor()

    print("✓ 连接成功！\n")

    # 查看有权限的数据库
    cursor.execute("SHOW DATABASES")
    databases = cursor.fetchall()
    print("可访问的数据库:")
    for db in databases:
        print(f"  - {db[0]}")

    # 查看用户权限
    cursor.execute("SHOW GRANTS FOR CURRENT_USER")
    grants = cursor.fetchall()
    print("\n当前用户权限:")
    for grant in grants:
        print(f"  {grant[0]}")

    # 尝试创建数据库
    print("\n尝试创建数据库 textdiff...")
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS textdiff CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("✓ 数据库创建成功")
    except pymysql.Error as e:
        print(f"✗ 无法创建数据库: {e}")
        print("  提示: 请联系数据库管理员创建数据库或授予创建权限")

    cursor.close()
    connection.close()

except pymysql.Error as e:
    print(f"✗ 连接失败: {e}")
