import json
from flask import Blueprint, request, Response
from applications.models.auth_model import User, db
from common.utils import validate, common_method, logs, ck_login
from common.utils.http import success_api, fail_api

Root_blu = Blueprint('root', __name__)


@Root_blu.route('/change_pwd/', methods=['POST'])
def Change_Pwd():
    """
    脚本：针对忘记密码紧急应对策略
    传参：{
      "uname": "root",
      "new_pwd":"rooter"
    }
    """
    if request.method == 'POST':
        data = request.get_data(as_text=True)
        json_data = json.loads(data)
        uname = validate.xss_escape(json_data.get('uname'))
        new_pwd = validate.xss_escape(json_data.get('new_pwd'))
        md5_pwd = common_method.md5(new_pwd)

        # ======== 未授权访问校验 ========
        if not ck_login.is_status('root'):
            return Response('root当前状态为离线，未授权访问！')
        # ================

        User.query.filter_by(uname=uname).update(
            {'uname': uname, 'pwd': md5_pwd, "status": False}
        )
        try:
            db.session.commit()
            logs.logger.info(f'用户（{uname}）修改个人信息成功, 即将登出')
            return success_api(msg='用户信息修改成功, 即将登出')
        except Exception as e:
            db.session.rollback()
            logs.logger.error(f"用户（{uname}）信息修改失败!\n"
                              f"报错信息{e}")
            return fail_api(msg=f"用户（{uname}）信息修改失败!\n"
                                f"报错信息{e}")


@Root_blu.route('/select_user_status/', methods=['GET'])
def Select_User_Status():
    """
    脚本：查询所有用户当前登陆状态
    """
    result = {}
    user_status_dict = {}
    user_list = User.query.all()
    for user in user_list:
        user_status_dict[user.uname] = user.status
    for name, status in user_status_dict.items():
        if status:
            msg = '登录'
        else:
            msg = '未登录'
        result[name] = msg

    return success_api(msg=f'{result}')
