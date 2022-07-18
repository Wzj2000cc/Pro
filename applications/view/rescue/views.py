import pymysql
import json
import numpy as np
import pandas as pd

from datetime import datetime
from flask import Blueprint, request, Response
from common.utils import ck_login, validate, common_method, logs
from applications.configs import config

Sql_blu = Blueprint('dataset', __name__)


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self, obj)


@Sql_blu.route('/sql_json/', methods=['POST'])
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
            return Response('该用户不存在，请注册或换账号登录！')
        if not ck_login.is_status(uname):
            return Response('当前状态为离线，请重新登录！')
        if not uname:
            return Response('用户名输入为空，请重新输入')
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
            count = len(result)

            end_time = datetime.now()
            result_time = end_time - start_time
            conn.close()
            logs.logger.info(f'用户（{uname}）运行查询成功，sql：{request_sql} ,耗时：{result_time}')
            return Response(result)
        except Exception as e:
            print(e)
            logs.logger.error(f'运行查询发生错误，报错信息提示为：{e}')
            return Response(f'sql语句可能存在语法错误！报错信息提示为：{e}')


@Sql_blu.route('/add/', methods=['POST'])
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
            return Response('该用户不存在，请注册或换账号登录！')
        if not ck_login.is_status(uname):
            return Response('当前状态为离线，请重新登录！')
        if not uname:
            return Response('用户名输入为空，请重新输入')
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
            return Response(f'用户{uname}保存数据集成功，耗时{result_time}')
        except Exception as E:
            print(E)
            logs.logger.error(f'保存数据集发生错误，报错信息为：{E}')


def insert_dataset(table_name, temp_data, column_str):
    """

    """
    conn = pymysql.connect(host=config.MYSQL_HOST, user=config.MYSQL_USERNAME, password=config.MYSQL_PASSWORD,
                           database=config.DATASET_DB_DATABASE, charset='utf8')
    cur = conn.cursor()
    insert_sql = f"INSERT INTO {table_name} ({column_str}) VALUES {temp_data}"
    cur.execute(insert_sql)
    conn.commit()
    cur.close()
    conn.close()