# Pro

#### 项目简介
> Pro 基于 Flask  的基础入门功能框架
>
> 项目旨在为python开发者提供一个入门框架的模板，成为您构建功能，快速开发....等应用时灵活，简单的工具
>
> 众人拾柴火焰高，欢迎pythoner参与项目~

#### 软件架构
```
​```
Pro
├─applications  # 应用
│  ├─common   # 公共文件
│  ├─configs  # 配置文件
│  │  └─ config.py  # 配置文件对象
│  ├─extensions  # 注册插件
│  ├─models  # 数据模型
│  └─views  # 视图部分
│     ├─AI     # 人工智能视图模块
│     ├─auth   # 用户应用视图模块
│     ├─tutle  # Pd视图模块
├─docs  # 文档说明（占坑）
├─migrations  # 迁移文件记录
├─requirement  # 依赖文件
├─test # 测试文件夹（占坑）
└─.env # 项目的配置文件

​```
```


#### 安装教程

```bash
# 下 载
git clone https://gitee.com/wang-zejun6/pro.git

# 安 装
pip install -r requirement\requirement-dev.txt

# 配 置
.env

```

#### 修改配置

```python
config.py
# MySql配置信息
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=audit_dataset_db
MYSQL_USERNAME=root
MYSQL_PASSWORD=xxxxxx

# Redis 配置
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
```

#### Venv 安装

```
python -m venv Pro
```

#### 运行项目

```bash
# 初 始 化 数 据 库

flask init
```

#### 配置执行信息

```
运行app.py文件
```

#### 命令行创建视图

```bash
# 示例

flask new --type view --name test/a

# 自动注册蓝图
# 访问http://127.0.0.1:5000/test/a/
```

#### 