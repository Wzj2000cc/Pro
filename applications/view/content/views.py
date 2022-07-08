import json
from flask import Blueprint, request, Response
from applications.models.content_model import Content, db
from common.utils import common_method, ck_login, validate
from common.utils.logs import logger

Content_blu = Blueprint('cnt', __name__)


@Content_blu.route('/addcnt/', methods=['POST'])
def Add_Content():
    """
    传参：{
      "uname": "Wzj",
      "content":"工程模型3摘要：ERP系统与营销系统系统变压器信息对比模型",
      "grade":"1",
      "view_id":"123456789"
    };
    {
      "uname": "Ysj",
      "content":",
      "grade":"2",
      "view":"Wzj",
      "view_content":"",
      "view_id":"123456789"
    }
    """
    if request.method == 'POST':
        data = request.get_data(as_text=True)
        json_data = json.loads(data)
        view_id = json_data.get('view_id')
        uname = validate.xss_escape(json_data.get('uname'))
        content = validate.xss_escape(json_data.get('content'))
        grade = validate.xss_escape(json_data.get('grade'))

        # ======== 安全登录校验 ========
        if ck_login.is_status(uname) is None:
            return Response('该用户不存在，请注册或换账号登录！')
        if not ck_login.is_status(uname):
            return Response('当前状态为离线，请重新登录！')
        if not uname:
            return Response('用户名输入为空，请重新输入')
        # ================
        view_content = None
        if not int(grade) == 1:
            view = validate.xss_escape(json_data.get('view'))
            view_content = validate.xss_escape(json_data.get('view_content'))
            content_view = Content(view_id=view_id, uname=uname, content=content, grade=grade, view=view,
                                   view_content=view_content)
        else:
            content_view = Content(view_id=view_id, uname=uname, content=content, grade=grade)
        try:
            db.session.add(content_view)
            db.session.commit()
            logger.info(f'用户（{uname}）对模型id为（{view_id}）评论：（{content}）') if int(grade) == 1 else logger.info(
                f'用户（{uname}）在模型id为{view_id}的（{view_content}）评论下进行了回复（{content}）')
            return Response('评论成功')
        except Exception as E:
            print(E)
            return Response(f'评论失败，报错信息：{E}')


@Content_blu.route('/delcnt/', methods=['POST'])
def Del_Content():
    """ 伪删除
    传参：{
      "uname": "Ysj",
      "content":"xxxxxxxxxxxxxxxxxx"
    }
    """
    if request.method == 'POST':
        data = request.get_data(as_text=True)
        json_data = json.loads(data)
        uname = validate.xss_escape(json_data.get('uname'))
        content = validate.xss_escape(json_data.get('content'))

        # ======== 安全登录校验 ========
        if ck_login.is_status(uname) is None:
            return Response('该用户不存在，请注册或换账号登录！')
        if not ck_login.is_status(uname):
            return Response('当前状态为离线，请重新登录！')
        if not uname:
            return Response('用户名输入为空，请重新输入')
        # ================

        del_objs = Content.query.filter_by(uname=uname, content=content).all()
        if del_objs:
            for del_obj in del_objs:
                if del_obj.grade == 1:
                    del2_objs = Content.query.filter_by(view_content=content).all()
                    for del2_obj in del2_objs:
                        del2_obj.log_status = True
                        del2_obj.good_num = 0
                del_obj.log_status = True
                del_obj.good_num = 0
                try:
                    db.session.commit()
                except Exception as E:
                    print(E)
                logger.info(f'用户（{uname}）删除评论（{content}）成功')
                return Response('删除成功')
        return Response('该评论不存在，无法删除')


@Content_blu.route('/changecnt/', methods=['POST'])
def change_Content():
    """ 点赞功能
    传参：{
      "uname": "Ysj",
      "content":"模型英文表名：ads_prj_szhsj_erpyxbyqxxdbmx_ws"
    }
    """
    if request.method == 'POST':
        data = request.get_data(as_text=True)
        json_data = json.loads(data)
        uname = validate.xss_escape(json_data.get('uname'))
        content = validate.xss_escape(json_data.get('content'))

        # ======== 安全登录校验 ========
        if ck_login.is_status(uname) is None:
            return Response('该用户不存在，请注册或换账号登录！')
        if not ck_login.is_status(uname):
            return Response('当前状态为离线，请重新登录！')
        if not uname:
            return Response('用户名输入为空，请重新输入')
        # ================

        contents = Content.query.filter_by(uname=uname, content=content).all()
        for con in contents:
            if not con.log_status:
                con.good_num += 1
                try:
                    db.session.commit()
                    logger.info(f'（{uname}）点赞评论（{content}）成功')
                    return Response('点赞成功')
                except Exception as E:
                    print(E)
            return Response('该评论不存在，无法删除')


@Content_blu.route('/selcnt/', methods=['GET'])
def select_Content():
    """
    传参：?uname=Wzj&view_id=123456789
    """
    if request.method == 'GET':
        uname = validate.xss_escape(request.args.get('uname'))
        view_id = validate.xss_escape(request.args.get('view_id'))

        # ======== 安全登录校验 ========
        if ck_login.is_status(uname) is None:
            return Response('该用户不存在，请注册或换账号登录！')
        if not ck_login.is_status(uname):
            return Response('当前状态为离线，请重新登录！')
        if not uname:
            return Response('用户名输入为空，请重新输入')
        # ================

        msg = ''
        contents_dic = {}
        sel_cons = Content.query.filter_by(view_id=view_id, uname=uname).all()
        for sel_con in sel_cons:
            contents_dic[sel_con.content] = sel_con.good_num
        for content, good_num in contents_dic.items():
            msg += f'评论：{content}, 点赞数：{good_num} \n'

        logger.info(f'用户（{uname}）在模型（{view_id}）共有（{len(contents_dic.items())}）条评论：\n'
                    f'{msg}')
        return Response(f'用户（{uname}）在模型（{view_id}）共有（{len(contents_dic.items())}）条评论：\n'
                        f'{msg}')
