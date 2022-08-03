# 导入SQLAlchemy模块
from flask_sqlalchemy import SQLAlchemy

# from sqlalchemy import
# 初始化db
db = SQLAlchemy()


class Modify(db.Model):
    __tablename__ = "dk_table_metadata_modify"  # 设置表名

    id = db.Column(db.INT, primary_key=True, autoincrement=True, nullable=False, comment="自增主键")
    database_name = db.Column(db.VARCHAR(128), nullable=False, comment="数据库名称")
    table_name = db.Column(db.VARCHAR(128), comment="表名称")
    column_name = db.Column(db.VARCHAR(128), index=True, comment="列名称")
    type_name = db.Column(db.VARCHAR(16), index=True, comment="table,column")
    comment = db.Column(db.VARCHAR(255), index=True, comment="表中文备注")
    create_time = db.Column(db.DateTime, index=True, comment="创建时间")
    create_user = db.Column(db.VARCHAR(64), index=True, comment="创建人")
