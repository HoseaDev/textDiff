# 数据库配置说明

## 当前情况

MySQL 服务器: `23.19.231.78:3306`
用户: `work`
可用数据库: `lianyanbao`

## 问题

`work` 用户当前只有 `lianyanbao` 数据库的权限，无法创建 `textdiff` 数据库。

## 解决方案

### 方案 1: 使用 lianyanbao 数据库（临时方案）

直接在 `lianyanbao` 数据库中创建表，表名添加前缀 `textdiff_` 以避免冲突：

```sql
-- 表名
textdiff_users
textdiff_documents
textdiff_versions
...
```

### 方案 2: 请管理员创建独立数据库（推荐）

联系数据库管理员执行以下 SQL：

```sql
-- 创建数据库
CREATE DATABASE textdiff CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 授权给 work 用户
GRANT ALL PRIVILEGES ON textdiff.* TO 'work'@'%';
FLUSH PRIVILEGES;
```

## 下一步

请选择一个方案：

1. **使用 lianyanbao 数据库**
   - 我会修改所有表名添加前缀 `textdiff_`
   - 立即可以开始开发

2. **等待管理员创建 textdiff 数据库**
   - 需要联系管理员
   - 然后重新运行初始化脚本

请告诉我选择哪个方案。
