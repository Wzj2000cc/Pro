import pymysql
import json
import numpy as np
import pandas as pd

from datetime import datetime
from flask import Blueprint, request, Response
from common.utils import ck_login, validate, common_method, logs
from applications.configs import config
from multiprocessing.pool import ThreadPool
from common.utils.http import success_api, fail_api

Data_blu = Blueprint('dataset', __name__)


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self, obj)


@Data_blu.route('/sql_json/', methods=['POST'])
def sql_json():
    """
    传参：{
      "uname": "Wzj",
      "sql":"select * from bp_dataset"
    }
    """
    if request.method == 'POST':
        data = request.get_data(as_text=True)
        json_data = json.loads(data)
        uname = validate.xss_escape(json_data.get('uname'))
        request_sql = json_data.get('sql')
        sql = common_method.find_unchinese(request_sql)

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
                               database=config.AUDIT_MYSQL_DATABASE, charset='utf8')
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
                result = list(json.dumps(data_list, ensure_ascii=False, cls=DateEncoder))

            end_time = datetime.now()
            result_time = end_time - start_time
            conn.close()
            logs.logger.info(f'用户（{uname}）运行查询成功，sql：{request_sql} ,耗时：{result_time}')
            return Response(result)
        except Exception as e:
            print(e)
            logs.logger.error(f'运行查询发生错误，报错信息提示为：{e}')
            return fail_api(msg=f'sql语句可能存在语法错误！报错信息提示为：{e}')


@Data_blu.route('/add/', methods=['POST'])
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
            create_sql = f'CREATE TABLE IF NOT EXISTS {table_name}({temp_str})'
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


@Data_blu.route('/find/', methods=['POST'])
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
            return success_api(msg=str(find_data))
        except Exception as e:
            logs.logger.info(f'查询失败，原因：{e}')
            return fail_api(msg=f'查询失败，原因：{e}')
