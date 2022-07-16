import pymysql
import json
import numpy as np
import pandas as pd

from datetime import datetime
from flask import Blueprint, request, Response
from common.utils import ck_login, validate, common_method, logs

Sql_blu = Blueprint('sql', __name__)


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
        conn = pymysql.connect(host='localhost', user='root', password='20001126', database='audit_dataset_db',
                               charset='utf8')
        logs.logger.info(f'用户：{uname} 已成功连接（audit_dataset_db）数据库')
        conn.cursor()
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
            logs.logger.info(f'用户（{uname}）进行了运行查询，sql：{request_sql} ,共耗时：{result_time}')
            return Response(result)
        except Exception as e:
            print(e)
            return Response(f'sql语句可能存在语法错误！具体报错信息：{e}')
