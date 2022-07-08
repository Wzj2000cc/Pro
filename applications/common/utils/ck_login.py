import datetime
from flask import Response
from applications.models.auth_model import db, User
from common.utils.logs import logger


# 用户登录状态
def is_status(uname):
    users = User.query.filter_by(uname=uname).all()
    if users:
        for user in users:
            state = user.status
            return state
    return None


# 注销登录
def del_login(uname, now_time):
    users = User.query.filter_by(uname=uname).all()
    for user in users:
        if user.status:
            user.status = False
            user.quit_time = now_time
            # noinspection PyBroadException
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()

            logger.info(f'用户（{uname}）注销成功')
            return Response('注销成功')
        logger.warning(f'用户（{uname}）当前为离线状态, 无需注销')
        return Response('您当前为离线状态，无需注销登录')


# 获取当前时间戳
def Current_Time():
    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return now_time
