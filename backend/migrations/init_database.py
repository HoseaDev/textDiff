"""
数据库初始化脚本
连接到 MySQL 并执行初始化 SQL
"""
import pymysql
import os
from pathlib import Path

# 数据库配置
DB_CONFIG = {
    'host': '23.19.231.78',
    'port': 3306,
    'user': 'work',
    'password': 's4TUPM.qXmfvAUu',
    'database': 'textdiff',  # 直接连接到 textdiff 数据库
    'charset': 'utf8mb4'
}

def init_database():
    """初始化数据库"""
    print("连接到 MySQL 服务器...")

    try:
        # 连接到 MySQL（不指定数据库）
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()

        print("✓ 成功连接到 MySQL 服务器")

        # 读取 SQL 文件
        sql_file = Path(__file__).parent / '001_init_mysql.sql'
        print(f"读取 SQL 文件: {sql_file}")

        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # 分割 SQL 语句（按分号分割，但保留完整的语句）
        statements = []
        current_statement = []
        in_delimiter = False

        for line in sql_content.split('\n'):
            # 跳过注释
            stripped = line.strip()
            if stripped.startswith('--') or not stripped:
                continue

            current_statement.append(line)

            # 检查是否是语句结束
            if ';' in line:
                statement = '\n'.join(current_statement)
                statements.append(statement)
                current_statement = []

        print(f"共 {len(statements)} 条 SQL 语句")

        # 执行 SQL 语句
        success_count = 0
        error_count = 0

        for i, statement in enumerate(statements, 1):
            statement = statement.strip()
            if not statement:
                continue

            try:
                cursor.execute(statement)
                connection.commit()
                success_count += 1

                # 打印进度
                if i % 5 == 0:
                    print(f"  进度: {i}/{len(statements)} 条语句执行完成")

            except pymysql.Error as e:
                error_count += 1
                print(f"  ⚠ 语句 {i} 执行失败: {e}")
                print(f"    语句: {statement[:100]}...")
                # 继续执行下一条

        print(f"\n执行完成:")
        print(f"  ✓ 成功: {success_count} 条")
        print(f"  ✗ 失败: {error_count} 条")

        # 验证表是否创建成功
        cursor.execute("""
            SELECT COUNT(*) as table_count
            FROM information_schema.tables
            WHERE table_schema = 'textdiff'
        """)
        table_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'textdiff'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]

        print(f"\n数据库 'textdiff' 包含 {table_count} 个表:")
        for table in tables:
            print(f"  - {table}")

        # 验证默认管理员用户
        cursor.execute("USE textdiff")
        cursor.execute("SELECT username, email FROM users WHERE is_superuser = TRUE")
        admin_users = cursor.fetchall()

        if admin_users:
            print(f"\n默认管理员账户:")
            for username, email in admin_users:
                print(f"  用户名: {username}")
                print(f"  邮箱: {email}")
                print(f"  密码: admin123 (请在生产环境修改)")

        print("\n✅ 数据库初始化完成！")

    except pymysql.Error as e:
        print(f"\n❌ 数据库初始化失败: {e}")
        return False

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
            print("\n连接已关闭")

    return True

if __name__ == '__main__':
    print("=" * 60)
    print("TextDiff 数据库初始化")
    print("=" * 60)
    init_database()
