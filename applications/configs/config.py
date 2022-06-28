from flask import Flask

from applications.view.auth.views import index_blu
from applications.view.AI.views import AI_blu
from applications.view.turtle.views import Turtle_blu
from applications.models.auth_model import db


def create_app():
    # 定义系统路径的变量
    # BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    # 初始化app 和manage.py文件关联
    app = Flask(__name__)
    app.debug = True
    # CORS(app, supports_credentials=True, resources=r'/*')
    # 注册蓝图
    app.register_blueprint(blueprint=index_blu, url_prefix='/index')
    app.register_blueprint(blueprint=AI_blu, url_prefix='/ai')
    app.register_blueprint(blueprint=Turtle_blu, url_prefix='/tur')

    # mysql 配置
    MYSQL_USERNAME = "root"
    MYSQL_PASSWORD = "rooter"
    MYSQL_HOST = "127.0.0.1"
    MYSQL_PORT = 3306
    MYSQL_DATABASE = "audit_dataset_db"

    app.config[
        'SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/" \
                                     f"{MYSQL_DATABASE}?charset=utf8mb4"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 设置session密钥
    app.config['SECRET_KEY'] = 'secret_key'
    # 初始化db
    db.init_app(app=app)

    app.config['ALLOWED_HOSTS'] = '192.168.43.176'

    return app
