from flask import Flask

from application.apps.auth.views import index_blu
from application.apps.AI.views import AI_blu
# from application.apps.auth.models import db
from application.models.auth_model import db


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
    # 配置mysql数据库
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:rooter@10.1.90.145:19103/dev_data_set?charset=utf8mb4'
    # app.config['SQLALCHEMY_BINDS'] = {
    #     'model_db': 'mysql+pymysql://root:rooter@10.1.90.145:19103/dev_zb_szhsjpt?charset=utf8mb4',          # 测试过mysql、sgrdb
    #     'dataset_db': 'mysql+pymysql://root:rooter@10.1.90.145:19103/dev_data_set?charset=utf8mb4',
    # }
    app.config[
        'SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:rooter@127.0.0.1:3306/audit_dataset_db?charset=utf8mb4'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 设置session密钥
    app.config['SECRET_KEY'] = 'secret_key'
    # 初始化db
    db.init_app(app=app)

    app.config['ALLOWED_HOSTS'] = '192.168.43.176'

    return app
