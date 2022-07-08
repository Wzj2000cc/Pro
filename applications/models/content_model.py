# 导入SQLAlchemy模块
from flask_sqlalchemy import SQLAlchemy

# from sqlalchemy import
# 初始化db
db = SQLAlchemy()


class Content(db.Model):
    __tablename__ = "content"  # 设置表名

    id = db.Column(db.INT, primary_key=True, comment="主键ID")
    view_id = db.Column(db.INT, nullable=False, comment="video/模型id")
    uname = db.Column(db.CHAR(100), index=True, comment="评论人名称")
    content = db.Column(db.VARCHAR(250), nullable=False, comment="评论内容")
    grade = db.Column(db.INT, nullable=False, default=0, comment="评论等级（1/2级）")
    view = db.Column(db.CHAR(100), index=True, comment="被评论人")
    view_content = db.Column(db.VARCHAR(250), index=True, comment="被评论人内容")
    good_num = db.Column(db.INT, nullable=False, default=0, comment="点赞数量")
    log_status = db.Column(db.Boolean, nullable=False, default=0, comment="记录评论状态，删除留底")
