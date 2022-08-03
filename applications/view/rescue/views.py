import json
import sys
import numpy as np
import pandas as pd
import pymysql

from datetime import datetime
from multiprocessing.pool import ThreadPool
from flask import Blueprint, request, Response

from applications.configs import config
from common.utils import ck_login, validate, common_method, logs
from common.utils.http import success_api, fail_api
from models.table_modify_model import Modify, db

Data_blu = Blueprint('dataset', __name__)


# class DateEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, datetime):
#             return obj.strftime("%Y-%m-%d %H:%M:%S")
#         else:
#             return json.JSONEncoder.default(self, obj)

# 查询数据json化
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        return json.JSONEncoder.default(self, obj)


@Data_blu.route('/sql_json', methods=['POST'])
def sql_json():
    """
    传参：{
      "uname": "Wzj",
      "sql": "select * from bp_dataset",
      "databases":
    }
    """

    if request.method == 'POST':
        data = request.get_data(as_text=True)
        json_data = json.loads(data)
        uname = validate.xss_escape(json_data.get('uname'))
        request_sql = json_data.get('sql')
        sql = common_method.find_unchinese(request_sql)
        databases = validate.xss_escape(json_data.get('databases'))

        # ======== 安全登录校验 ========
        if ck_login.is_status(uname) is None:
            return fail_api(msg='该用户不存在，请注册或换账号登录！')
        if not ck_login.is_status(uname):
            return fail_api(msg='当前状态为离线，请重新登录！')
        if not uname:
            return fail_api(msg='用户名输入为空，请重新输入')
        # ================

        start_time = datetime.now()
        conn = pymysql.connect(host=config.MYSQL_HOST, user=config.MYSQL_USERNAME, password=config.MYSQL_PASSWORD,
                               database=databases, charset='utf8')
        logs.logger.info(f'用户：{uname} 已成功连接（audit_dataset_db）数据库')
        # conn.cursor()
        try:
            df = pd.read_sql(sql, conn)
            column_list = list(df.columns)
            df1 = np.array(df)
            result = None
            data_list = []
            for row in df1:
                data_dic = dict(zip(column_list, list(row)))
                data_list.append(data_dic)
                result = list(json.dumps(data_list, ensure_ascii=False, cls=MyEncoder, indent=4))

            end_time = datetime.now()
            result_time = end_time - start_time
            conn.close()
            logs.logger.info(f'用户（{uname}）运行查询成功，sql：{request_sql} ,耗时：{result_time}')
            return Response(result)
        except Exception as e:
            print(e)
            logs.logger.error(f'运行查询发生错误，报错信息提示为：{e}')
            return fail_api(msg=f'sql语句可能存在语法错误！报错信息提示为：{e}')


@Data_blu.route('/add', methods=['POST'])
def add():
    """
    传参：{
      "uname": "Wzj",
      "table_name": "",
      "data" : ""
    }
    """
    if request.method == 'POST':
        data = request.get_data(as_text=True)
        json_data = json.loads(data)
        uname = validate.xss_escape(json_data.get('uname'))
        table_name = validate.xss_escape(json_data.get('table_name'))
        request_data = json_data.get('data')

        # ======== 安全登录校验 ========
        if ck_login.is_status(uname) is None:
            return fail_api(msg='该用户不存在，请注册或换账号登录！')
        if not ck_login.is_status(uname):
            return fail_api(msg='当前状态为离线，请重新登录！')
        if not uname:
            return fail_api(msg='用户名输入为空，请重新输入')
        # ================

        # 筛选出建表字段
        temp_str = ''
        column_str = ''
        for column in request_data[0]:
            column_str += column + ','
            temp_str += column + ' longtext,\n'
        column_str = column_str[:-1]
        temp_str = temp_str[:-2]

        try:
            # 插入保存数据表数据
            temp_data = ''
            for receive_data in request_data:
                temp_data += '('
                for data in receive_data.values():
                    temp_data += "'" + str(data) + "'" + ','
                temp_data = temp_data[:-1]
                temp_data += '),\n'
            temp_data = temp_data[:-2]

            start_time = datetime.now()
            conn = pymysql.connect(host=config.MYSQL_HOST, user=config.MYSQL_USERNAME, password=config.MYSQL_PASSWORD,
                                   database=config.DATASET_DB_DATABASE, charset='utf8')
            logs.logger.info(f'用户：{uname} 已成功连接（audit_dataset_db）数据库')
            cur = conn.cursor()
            # 创建表 table_name
            create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (YL_ID int PRIMARY KEY AUTO_INCREMENT,{temp_str})"
            cur.execute(create_sql)
            conn.commit()
            cur.close()
            conn.close()
            # 插入数据 temp_data
            insert_dataset(table_name, temp_data, column_str)

            end_time = datetime.now()
            result_time = end_time - start_time
            logs.logger.info(f'用户{uname}保存数据集成功，耗时{result_time}')
            return success_api(msg=f'用户{uname}保存数据集成功，耗时{result_time}')
        except Exception as E:
            print(E)
            logs.logger.error(f'保存数据集发生错误，报错信息为：{E}')
            return fail_api(msg=f'保存数据集发生错误，报错信息为：{E}')


def insert_dataset(table_name, temp_data, column_str):
    """
    json形式数据插入表 table_name
    """
    conn = pymysql.connect(host=config.MYSQL_HOST, user=config.MYSQL_USERNAME, password=config.MYSQL_PASSWORD,
                           database=config.DATASET_DB_DATABASE, charset='utf8')
    cur = conn.cursor()
    insert_sql = f"INSERT INTO {table_name} ({column_str}) VALUES {temp_data}"
    cur.execute(insert_sql)
    conn.commit()
    cur.close()
    conn.close()


def find_common(pks, name):
    data_list = []
    for data in pks:
        if name in data['TABLE_NAME'] or name in data['TABLE_COMMENT']:
            data_list.append(data)
    return data_list


@Data_blu.route('/find', methods=['POST'])
def Find():
    """
    采用双进程模式 ！！！
    传参：{
      "uname": "Wzj",
      "table_name": " "
    }
    """
    if request.method == 'POST':
        data = request.get_data(as_text=True)
        json_data = json.loads(data)
        uname = validate.xss_escape(json_data.get('uname'))
        table_name = validate.xss_escape(json_data.get('table_name'))

        # ======== 安全登录校验 ========
        if ck_login.is_status(uname) is None:
            return fail_api(msg='该用户不存在，请注册或换账号登录！')
        if not ck_login.is_status(uname):
            return fail_api(msg='当前状态为离线，请重新登录！')
        if not uname:
            return fail_api(msg='用户名输入为空，请重新输入')
        # ================

        conn = pymysql.connect(host=config.MYSQL_HOST, user=config.MYSQL_USERNAME, password=config.MYSQL_PASSWORD,
                               database=config.TABLE_DATABASE, charset='utf8')
        cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
        select_sql = f"SELECT TABLE_NAME,TABLE_COMMENT FROM TABLES WHERE TABLE_TYPE ='BASE TABLE'"
        cur.execute(select_sql)
        result = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()

        length = int(len(result) / 2)
        pks1 = result[:length]
        pks2 = result[length:]

        try:
            pool = ThreadPool(processes=2)
            async_result1 = pool.apply_async(find_common, args=(pks1, table_name))
            async_result2 = pool.apply_async(find_common, args=(pks2, table_name))

            return_val1 = async_result1.get()
            return_val2 = async_result2.get()
            find_data = return_val1 + return_val2

            logs.logger.info(f"用户{uname}查询表名'{table_name}',查询结果为：{find_data}")
            # return success_api(msg=str(find_data))
            return Response(f'查询结果为：{find_data}')
        except Exception as e:
            logs.logger.info(f'查询失败，原因：{e}')
            return fail_api(msg=f'查询失败，原因：{e}')


def show_change_table_comment(table_name):
    comments = Modify.query.filter_by(table_name=table_name, type_name='table').first()
    if comments:
        comment = comments.comment
        is_table_comment_status = True
    else:
        conn = pymysql.connect(host=config.MYSQL_HOST, user=config.MYSQL_USERNAME, password=config.MYSQL_PASSWORD,
                               database=config.TABLE_DATABASE, charset='utf8')
        cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
        select_sql = f"SELECT TABLE_COMMENT FROM TABLES " \
                     f"WHERE TABLE_TYPE ='BASE TABLE' AND TABLE_NAME ='{table_name}'"
        cur.execute(select_sql)
        comment = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        is_table_comment_status = False
    return comment, is_table_comment_status


def show_change_column_comment(table_name, column_name):
    comment = None
    comments = Modify.query.filter_by(table_name=table_name, column_name=column_name, type_name='column').first()
    if comments:
        comment = comments.comment
    return comment


@Data_blu.route('/tables/', methods=['POST'])
def Show_Tables():
    """
    拖表根据表名提供表信息
    "uname": "Wzj",
    "table_name": " "
    """
    if request.method == 'POST':
        data = request.get_data(as_text=True)
        json_data = json.loads(data)
        uname = validate.xss_escape(json_data.get('uname'))
        table_name = validate.xss_escape(json_data.get('table_name'))

        # ======== 安全登录校验 ========
        if ck_login.is_status(uname) is None:
            return fail_api(msg='该用户不存在，请注册或换账号登录！')
        if not ck_login.is_status(uname):
            return fail_api(msg='当前状态为离线，请重新登录！')
        if not uname:
            return fail_api(msg='用户名输入为空，请重新输入')
        # ================

        conn = pymysql.connect(host=config.MYSQL_HOST, user=config.MYSQL_USERNAME, password=config.MYSQL_PASSWORD,
                               database=config.TABLE_DATABASE, charset='utf8')
        cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
        select_column_sql = f"SELECT COLUMN_NAME,COLUMN_COMMENT,COLUMN_KEY FROM COLUMNS " \
                            f"WHERE TABLE_NAME = '{table_name}'"
        cur.execute(select_column_sql)
        result = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()

        payload_columns = []
        primary_key = []
        foreign_keys = []
        for column in result:
            if column['COLUMN_KEY'] == 'PRI':
                primary_key.append(column)
            del column['COLUMN_KEY']
            column['is_column_comment_status'] = False
            if show_change_column_comment(table_name, column['COLUMN_NAME']):
                column['COLUMN_COMMENT'] = show_change_column_comment(table_name, column['COLUMN_NAME'])
                column['is_column_comment_status'] = True
            payload_columns.append(column)

        tbl = {
            'name': table_name,
            'columns': payload_columns,
            'primaryKey': primary_key,
            'foreignKeys': foreign_keys,
            'table_comment': show_change_table_comment(table_name=table_name)[0],
            'is_table_comment_status': show_change_table_comment(table_name=table_name)[1]
        }

        logs.logger.info(f"用户{uname}拖表{table_name}，表结构为{tbl}")
        return Response(json.dumps(tbl))


# 正则校验中文备注是否只包含中文
def check_contain_chinese(check_str):
    for ch in check_str.encode('utf-8').decode('utf-8'):
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False


@Data_blu.route('/save/', methods=['POST'])
def Save_Comment():
    """
    保存表或表字段的注释
    输入的 form 参数:
{
    "uname"  : "Wzj",
    "database" : " ",
    "table_name":"table_name",
    "msg" : [{"column":"table_name","comment": "用户信息表","is_change_table": 1 },
    {"column":"uname","comment": "用户姓名","is_change_table": 0},
    {"column":"count","comment": "账号登录次数","is_change_table": 0}
    ...............]
}
    form参数说明
        is_change_table 是否修改表的注释：1 修改表的注释，0 修改列的注释
    """
    if request.method == 'POST':
        data = request.get_data(as_text=True)
        json_data = json.loads(data)
        uname = validate.xss_escape(json_data.get('uname'))
        database = validate.xss_escape(json_data.get('database'))
        table_name = validate.xss_escape(json_data.get('table_name'))
        msg = json_data.get('msg')

        # ======== 安全登录校验 ========
        if ck_login.is_status(uname) is None:
            return fail_api(msg='该用户不存在，请注册或换账号登录！')
        if not ck_login.is_status(uname):
            return fail_api(msg='当前状态为离线，请重新登录！')
        if not uname:
            return fail_api(msg='用户名输入为空，请重新输入')
        # ================

        for cmt_dict in msg:
            if not check_contain_chinese(cmt_dict['comment']):
                if cmt_dict['is_change_table']:
                    return fail_api(msg=f"表名{cmt_dict['column']}备注存在特殊字符！")
                elif not cmt_dict['is_change_table']:
                    return fail_api(msg=f"字段{cmt_dict['column']}备注存在特殊字符！")

        time = ck_login.Current_Time()
        for comment_dict in msg:

            if comment_dict['is_change_table'] == 1:
                if Modify.query.filter_by(table_name=comment_dict['column'], type_name='table').first():
                    Modify.query.filter_by(table_name=comment_dict['column']).update(
                        {"comment": comment_dict['comment']}
                    )
                else:
                    dk_modify = Modify(database_name=database, table_name=comment_dict['column'], column_name='',
                                       type_name='table', comment=comment_dict['comment'], create_time=time,
                                       create_user=uname)
                    db.session.add(dk_modify)
                db.session.commit()
                logs.logger.info(f"用户（{uname}）修改表（{comment_dict['column']}）备注为（{comment_dict['comment']}）")

            elif comment_dict['is_change_table'] == 0:
                if Modify.query.filter_by(column_name=comment_dict['column'], type_name='column').first():
                    Modify.query.filter_by(column_name=comment_dict['column']).update(
                        {"comment": comment_dict['comment']}
                    )
                else:
                    dk_modify = Modify(database_name=database, table_name=table_name,
                                       column_name=comment_dict['column'],
                                       type_name='column', comment=comment_dict['comment'], create_time=time,
                                       create_user=uname)
                    db.session.add(dk_modify)
                db.session.commit()
                logs.logger.info(f"用户（{uname}）修改字段（{comment_dict['column']}）备注为（{comment_dict['comment']}）")
        return success_api(msg='保存成功')


@Data_blu.route('/reset/', methods=['POST'])
def reset_comment():
    """
    重置表或字段的注释
    输入的 form 参数:
    {
    "uname"  : "Wzj",
    "database" : "audit_dataset_db",
    "msg" : {"table_name" :"table_name"},
    "is_change_table": 1
    }
    {
    "uname"  : "Wzj",
    "database" : "audit_dataset_db",
    "msg" :  {"table_name" :"table_name","column" : "uname"},
    "is_change_table": 0
    }
    form参数说明
        is_change_table 是否修改表的注释：1 修改表的注释，0 修改列的注释
    """
    if request.method == 'POST':
        data = request.get_data(as_text=True)
        json_data = json.loads(data)
        uname = validate.xss_escape(json_data.get('uname'))
        database = validate.xss_escape(json_data.get('database'))
        msg = json_data.get('msg')
        is_change_table = json_data.get('is_change_table')

        # ======== 安全登录校验 ========
        if ck_login.is_status(uname) is None:
            return fail_api(msg='该用户不存在，请注册或换账号登录！')
        if not ck_login.is_status(uname):
            return fail_api(msg='当前状态为离线，请重新登录！')
        if not uname:
            return fail_api(msg='用户名输入为空，请重新输入')
        # ================

        if is_change_table == 1:
            table_view = Modify.query.filter_by(database_name=database, table_name=msg['table_name'],
                                                type_name='table').first()
            db.session.delete(table_view)
            db.session.commit()

            conn = pymysql.connect(host=config.MYSQL_HOST, user=config.MYSQL_USERNAME, password=config.MYSQL_PASSWORD,
                                   database=config.TABLE_DATABASE, charset='utf8')
            logs.logger.info(f'用户：{uname} 已成功连接（{database}）数据库')
            cur = conn.cursor()

            # 重置删除modify表记录后重新去information_schema.TABLE表获取原注释并返回
            select_table_sql = f"SELECT TABLE_COMMENT FROM TABLES " \
                               f"WHERE TABLE_TYPE ='BASE TABLE' AND TABLE_NAME ='{msg['table_name']}'"
            cur.execute(select_table_sql)
            comment = cur.fetchall()
            conn.commit()
            cur.close()
            conn.close()
            result = {"table_name": msg['table_name'], "comment": comment}

            return Response(f'{result}')

        elif is_change_table == 0:
            column_view = Modify.query.filter_by(database_name=database, table_name=msg['table_name'],
                                                 column_name=msg['column'], type_name='column').first()
            db.session.delete(column_view)
            db.session.commit()

            conn = pymysql.connect(host=config.MYSQL_HOST, user=config.MYSQL_USERNAME, password=config.MYSQL_PASSWORD,
                                   database=config.TABLE_DATABASE, charset='utf8')
            logs.logger.info(f'用户：{uname} 已成功连接（{database}）数据库')
            cur = conn.cursor()

            # 重置删除modify表记录后重新去information_schema.TABLE表获取原注释并返回
            select_column_sql = f"SELECT COLUMN_COMMENT FROM COLUMNS WHERE TABLE_NAME = '{msg['table_name']}'" \
                                f" AND COLUMN_NAME = '{msg['column']}'"
            cur.execute(select_column_sql)
            result = cur.fetchall()
            conn.commit()
            cur.close()
            conn.close()
            connect = {"table_name": msg['table_name'], "column": msg['column'],
                       "comment": result}

            return Response(f'{connect}')
