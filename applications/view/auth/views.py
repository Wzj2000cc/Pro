import json

from flask import Blueprint, request, Response, session
from applications.models.auth_model import User, db
# from applications.models.content_model import db
from common.utils import common_method, ck_login, validate
from common.utils.logs import logger
from common.utils.http import success_api, fail_api

index_blu = Blueprint('index', __name__, url_prefix='/index')

role_dict = {"admin": "管理员", "user": "审计用户", "person": "部门专责"}
weight_dict = {"admin": 3, "user": 1, "person": 2, "None": 1}


@index_blu.route('/create_db')
def Create_DB():
    """
    创建数据库
    """
    db.create_all()
    logger.info('数据库创建成功')
    return success_api(msg='create all')


@index_blu.route('/drop_db')
def Drop_DB():
    """
    删除数据库
    """
    db.drop_all()
    logger.info('数据库删除成功')
    return success_api(msg='drop all')


# 注册接口
@index_blu.route('/register', methods=['POST'])
def Register():
    """
    传参：{
      "uname": "root",
      "pwd":"rooter",
      "source": "155"
    }
    """
    if request.method == 'POST':
        data = request.get_data(as_text=True)
        # json_data = request.args
        json_data = json.loads(data)
        uname = validate.xss_escape(json_data.get('uname'))
        pwd = validate.xss_escape(json_data.get('pwd'))
        source = validate.xss_escape(json_data.get('source'))
        now_time = ck_login.Current_Time()

        if not (uname and pwd):
            logger.warning('用户名或密码为空，请规范输入')
            return fail_api(msg='用户名或密码为空，请规范输入')

        ciphertext = common_method.md5(pwd)
        user = User(uname=uname, pwd=ciphertext, source=source, start_time=now_time)

        try:
            db.session.add(user)
            db.session.commit()
            logger.info(f"用户:{uname} 注册成功!")
            return success_api(msg='用户注册成功, 请尽快联系管理员进行角色授权')
        except Exception as e:
            logger.error(f"用户:{uname} 注册失败!\n"
                         f"具体原因：{e}")
            return fail_api(f'用户:{uname} 注册失败 \n'
                            f'报错信息：{e}')


@index_blu.route('/getCaptcha')
def get_captcha():
    resp, code = common_method.get_captcha()
    session["code"] = code
    print(f'验证码{code}')
    return resp


# 登录接口
@index_blu.route('/login', methods=['POST'])
def Login():
    """
    登录前先行调用'/index/getCaptcha/'接口获取验证码！！！
    传参：{
    "uname": "root",
    "pwd":"rooter",
    "code":"gip5"
}
    """

    if request.method == 'POST':
        data = request.get_data(as_text=True)
        json_data = json.loads(data)
        uname = validate.xss_escape(json_data.get('uname'))
        pwd = validate.xss_escape(json_data.get('pwd'))
        codes = validate.xss_escape(json_data.get('code'))
        now_time = ck_login.Current_Time()
        user_list = User.query.filter_by(uname=uname).all()
        code = session.get("code", None)

        if not user_list:
            return fail_api(msg=f'用户（{uname}）不存在，请注册或换账号登录！')

        for user in user_list:
            if uname == user.uname and common_method.md5(pwd) == user.pwd:
                if codes == code:
                    user.status = True
                    user.count += 1
                    user.last_time = now_time
                    try:
                        db.session.commit()
                    except Exception as e:
                        logger.error(f"用户:{uname} 登录时出错!\n"
                                     f"具体原因：{e}")

                    logger.info(f'（{uname}）用户已登录Pro平台')
                    return success_api(msg='当前登录账户：{}, 欢迎登录Pro平台！'.format(uname))
                return fail_api(msg='验证码错误')
            return fail_api(msg='用户名或密码错误')


# 注销接口
@index_blu.route('/logout', methods=['GET'])
def LogOut():
    """
    传参：?uname=Wzj
    """
    if request.method == 'GET':
        uname = validate.xss_escape(request.args.get('uname'))
        now_time = ck_login.Current_Time()

        # ======== 安全登录校验 ========
        if ck_login.is_status(uname) is None:
            return fail_api(msg='该用户不存在，请注册或换账号登录！')
        if not ck_login.is_status(uname):
            return fail_api(msg='当前状态为离线，请重新登录！')
        if not uname:
            return fail_api(msg='用户名输入为空，请重新输入')
        # ================

        try:
            return ck_login.del_login(uname, now_time)
        except Exception as e:
            logger.error(f"用户（{uname}）注销失败!\n"
                         f"具体原因：{e}")
            return fail_api(msg='系统异常，请联系管理员')


# 查询展示接口（快排）
@index_blu.route('/select', methods=['GET'])
def Select_User():
    """
    传参：?uname=Wzj
    """
    if request.method == 'GET':
        uname = validate.xss_escape(request.args.get('uname'))

        # ======== 安全登录校验 ========
        if ck_login.is_status(uname) is None:
            return fail_api(msg='该用户不存在，请注册或换账号登录！')
        if not ck_login.is_status(uname):
            return fail_api(msg='当前状态为离线，请重新登录！')
        if not uname:
            return fail_api(msg='用户名输入为空，请重新输入')
        # ================

        users = User.query.filter_by(uname=uname).all()
        user_count = User.query.count()  # 查询有多少个⽤户
        user1 = User.query.first()  # 查询第1个⽤户
        user_list = User.query.all()  # 查询所有⽤户数据
        content = '感谢您对本平台的支持!'

        # ======== 快排使用 ========
        source_list = []
        report = []
        for user in user_list:
            source_dict = {'name': user.uname, 'source': user.source}
            source_list.append(source_dict)
            report.append(int(user.source))
        common_method.quick_sort(report, 0, len(report) - 1)
        # ================

        rank = None
        # sort_source = sorted(source_list, key=lambda x: x['source'], reverse=True)
        for source in source_list:
            if uname == source['name']:
                # rank = sort_source.index(source) + 1
                rank = report.index(source['source']) + 1

        global role_dict
        current = None
        for user in users:
            for idx, user1_count in enumerate(user_list):
                if user1_count.id == user.id:
                    current = idx + 1
                    if current < 3:
                        content = '稍后我们会联系您来发放奖品!'
            return Response(
                '用户名：{} \n'
                '当前身份{} \n'
                '考核成绩单：{} \n'
                '您的考核成绩：{} \n'
                '您的考核名次：{} \n'
                '账号创建时间：{} \n'
                '上次登录时间：{} \n'
                '平台总用户量：{} \n'
                '首位注册的用户为：{} \n'
                '您是第{}位注册的用户，{}'.format(
                    user.uname,
                    role_dict.get(user.role),
                    report,
                    user.source,
                    rank,
                    user.start_time,
                    user.last_time,
                    user_count,
                    user1.uname,
                    current,
                    content)
            )


# 用户信息修改
@index_blu.route('/change', methods=['PUT'])
def Change_User():
    """
    传参：{
      "uname": "Zj",
      "change_name": "Wzj",
      "change_pwd":"20001126",
      "change_source":"170"
    }
    """
    if request.method == 'PUT':
        data = request.get_data()
        json_data = json.loads(data)
        uname = validate.xss_escape(json_data.get('uname'))
        change_uname = validate.xss_escape(json_data.get('change_name'))
        change_pwd = validate.xss_escape(json_data.get('change_pwd'))
        change_source = validate.xss_escape(json_data.get('change_source'))
        if not (uname and change_uname):
            return Response('请重新输入要删除的用户名或修改后的用户名')

        # ======== 安全登录校验 ========
        if ck_login.is_status(uname) is None:
            return fail_api(msg='该用户不存在，请注册或换账号登录！')
        if not ck_login.is_status(uname):
            return fail_api(msg='当前状态为离线，请重新登录！')
        if not uname:
            return fail_api(msg='用户名输入为空，请重新输入')
        # ================

        if change_uname and common_method.md5(change_pwd) and change_source:
            User.query.filter_by(uname=uname).update(
                {"uname": change_uname, "pwd": common_method.md5(change_pwd),
                 "source": change_source, "status": False}
            )
            try:
                db.session.commit()
                logger.info(f'用户（{uname}）修改个人信息成功, 即将登出')
                return success_api('用户信息修改成功, 即将登出')
            except Exception as e:
                db.session.rollback()
                logger.error(f"用户（{uname}）信息修改失败!\n"
                             f"报错信息{e}")

        logger.warning(f'用户（{uname}）修改信息填写不完整')
        return fail_api(msg='用户修改信息填写不完整')


# 删除用户
@index_blu.route('/del', methods=['GET'])
def Del_User():
    """
    传参：?uname=Wzj&del_name=root
    """
    if request.method == 'GET':
        uname = validate.xss_escape(request.args.get('uname'))
        del_name = validate.xss_escape(request.args.get('del_name'))

        # ======== 安全登录校验 ========
        if ck_login.is_status(uname) is None:
            return fail_api(msg='该用户不存在，请注册或换账号登录！')
        if not ck_login.is_status(uname):
            return fail_api(msg='当前状态为离线，请重新登录！')
        if not uname:
            return fail_api(msg='用户名输入为空，请重新输入')
        # ================

        global weight_dict, role_dict
        del_user = None

        users = User.query.filter_by(uname=uname).all()
        del_users = User.query.filter_by(uname=del_name).all()

        for del_user in del_users:
            pass
        for user in users:
            if weight_dict.get(user.role) > weight_dict.get(del_user.role):
                try:
                    db.session.delete(user)
                    db.session.commit()
                    logger.info(f'{role_dict.get(user.role)}（{user.uname}）将用户（{del_user.uname}）删除成功!')
                    return Response(f'{role_dict.get(user.role)}（{user.uname}）将用户（{del_user.uname}）删除成功!')
                except Exception as e:
                    logger.error(f"用户（{uname}）删除失败!\n"
                                 f"报错信息{e}")
            else:
                logger.info(f'{role_dict.get(user.role)}（{user.uname}）将用户（{del_user.uname}）删除成功!')
                return fail_api(msg=f'{role_dict.get(user.role)}（{user.uname}）将用户（{del_user.uname}）删除成功!')


@index_blu.route('/role', methods=['POST'])
def Role():
    """
    传参：?uname=Wzj&rname=root&role=管理员
    """
    if request.method == 'POST':
        uname = validate.xss_escape(request.args.get('uname'))
        rname = validate.xss_escape(request.args.get('rname'))
        role = validate.xss_escape(request.args.get('role'))
        users = User.query.filter_by(uname=uname).all()
        dusers = User.query.filter_by(uname=rname).all()

        # ======== 安全登录校验 ========
        if ck_login.is_status(uname) is None:
            return fail_api(msg='该用户不存在，请注册或换账号登录！')
        if not ck_login.is_status(uname):
            return fail_api(msg='当前状态为离线，请重新登录！')
        if not uname:
            return fail_api(msg='用户名输入为空，请重新输入')
        # ================

        global weight_dict, role_dict
        drole = None
        urole = None
        old_drole = None
        user = None
        duser = None
        old_role = None

        for k, v in role_dict.items():
            if v == role:
                drole = k
        for user in users:
            urole = role_dict.get(user.role)
        for duser in dusers:
            old_drole = role_dict.get(duser.role)
            old_role = duser.role

        if weight_dict.get(user.role) is None:
            return fail_api(msg='当前登录用户无身份，请联系管理员进行赋权或更换账户')
        if role == old_drole:
            return fail_api(msg='权限未变动，请重新设置')

        if weight_dict.get(duser.role) is None or weight_dict.get(user.role) > weight_dict.get(duser.role):
            duser.role = drole
            try:
                db.session.commit()
                if not old_role:
                    logger.info(f'{urole}（{user.uname}）将用户（{duser.uname}）由无身份改为{role}')
                    return success_api(f'{urole}（{user.uname}）将用户（{duser.uname}）由无身份改为{role}')
                logger.info(f'{urole}（{user.uname}）将用户（{duser.uname}）身份由{old_drole}改为{role}')
                return success_api(f'{urole}（{user.uname}）将用户（{duser.uname}）身份由{old_drole}改为{role}')
            except Exception as e:
                logger.error(f"{urole}（{user}）修改用户（{duser}）权限失败\n"
                             f"报错信息{e}")
        else:
            return success_api(f'当前登录账户身份：{urole}，没有修改目标角色的权限')


@index_blu.route('/sql', methods=['POST'])
def Sql():
    data = request.get_data()
    uname = validate.xss_escape(json.loads(data).get('uname'))

    # ======== 安全登录校验 ========
    if ck_login.is_status(uname) is None:
        return fail_api(msg='该用户不存在，请注册或换账号登录！')
    if not ck_login.is_status(uname):
        return fail_api(msg='当前状态为离线，请重新登录！')
    if not uname:
        return fail_api(msg='用户名输入为空，请重新输入')
    # ================

    old_sql = json.loads(data).get('sql')
    # old_sql = "# config1 script begin. \n" \
    #         "import MySQLdb\n"\
    #         "import json\n"\
    #         "import collections\n"\
    #         "import pandas as pd\n"\
    #         "from superset import dataframe\n"\
    #         "conn = MySQLdb.connect(\n"\
    #         "    db='szhsjpt',\n"\
    #         "    host='10.1.90.145',\n"\
    #         "    port=19103,\n"\
    #         "    user='root',\n"\
    #         "    password='rooter',\n"\
    #         "    charset='utf8')\n"\
    #         "df = pd.read_sql('SELECT id, -- 序号 name -- 姓名 FROM szhsjpt.bd_common_config where id == 1', con=conn)\n"\
    #         "old_columns_names = [cl for cl in df.columns]\n"\
    #         "new_columns_names = dataframe.dedup(old_columns_names)\n"\
    #         "df.columns = new_columns_names\n"\
    #         "df_string = df.to_json(orient='records', force_ascii=False)\n"\
    #         "print(df_string)\n"\
    #         "# config1 script end."
    if '--' in old_sql:
        new_sql = common_method.find_unchinese(old_sql)
    else:
        new_sql = old_sql

    logger.info(f'用户{uname} 执行sql优化操作 \n'
                f'待优化sql：{old_sql} \n'
                f'优化后sql：{new_sql}')
    return success_api(msg=new_sql)
