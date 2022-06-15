# 导入SQLAlchemy模块
from flask_sqlalchemy import SQLAlchemy

# from sqlalchemy import
# 初始化db
db = SQLAlchemy()


class Code_two(db.Model):
    __tablename__ = "code_two"  # 设置表名

    id = db.Column(db.INT, primary_key=True, comment="主键ID")
    code_name = db.Column(db.CHAR(100), index=True, nullable=False, comment="二维码名称")
    to_path = db.Column(db.VARCHAR(250), nullable=False, comment="指向路径")
    svg_path = db.Column(db.VARCHAR(250), nullable=False, comment="二维码路径")
    png_base64 = db.Column(db.VARCHAR(250), nullable=False, comment="svg转png二进制码")

    usercode = db.Column(db.INT, db.ForeignKey('table_name.id'))


class User(db.Model):
    __tablename__ = "table_name"  # 设置表名

    id = db.Column(db.INT, primary_key=True, comment="主键ID")
    uname = db.Column(db.CHAR(100), index=True, unique=True, comment="姓名")
    pwd = db.Column(db.VARCHAR(250), nullable=False, comment="密码")
    role = db.Column(db.VARCHAR(10), comment="角色")
    count = db.Column(db.INT, nullable=False, default=0, comment="登录次数")
    status = db.Column(db.Boolean, nullable=False, default=0, comment="登录状态")
    source = db.Column(db.Float, nullable=False, default=0, comment='学生结业成绩')
    start_time = db.Column(db.DateTime, nullable=False, comment='账号创建时间')
    last_time = db.Column(db.DateTime, comment='用户上次登录时间')
    quit_time = db.Column(db.DateTime, comment='用户退出登录时间')

    code_twos = db.relationship('Code_two', backref='user')

    # def __init__(self, uname):
    #     self.name = uname

    # 定义保存数据的方法 后面视图好使用
    def save(self):
        db.session.add(self)
        db.session.commit()
