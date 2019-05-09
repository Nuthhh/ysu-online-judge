#!/usr/bin/python3

import pymysql


# 根据题目id获取所有测试用例
def select_question_test_list(question_id):
    # 打开数据库连接
    db = pymysql.connect(
        host='222.30.145.2',
        port=3306,
        user='ysu2019',
        passwd='ysu2019!',
        db='ysu',
        charset='utf8'
    )
    # 创建一个游标对象 cursor
    cursor = db.cursor()
    # 执行sql
    cursor.execute("SELECT question_in,question_out FROM ysu_question_test WHERE question_id = %s", question_id)
    # 获取执行结果
    data = cursor.fetchall()
    # 关闭数据库
    db.close()
    return data


# 根据题目id获取运行时间、运行内存要求
def get_question_info(question_id):
    db = pymysql.connect(
        host='222.30.145.2',
        port=3306,
        user='ysu2019',
        passwd='ysu2019!',
        db='ysu',
        charset='utf8'
    )
    cursor = db.cursor()
    cursor.execute("SELECT time,memory FROM ysu_question WHERE question_id= %s", question_id)
    data = cursor.fetchone()
    db.close()
    return data


# 将评测结果写入数据库
def insert_exe_result(exe_result):
    # 打开数据库连接
    db = pymysql.connect(
        host='222.30.145.2',
        port=3306,
        user='ysu2019',
        passwd='ysu2019!',
        db='ysu',
        charset='utf8'
    )
    # 创建一个游标对象 cursor
    cursor = db.cursor()
    sql = "INSERT INTO ysu_exe_result VALUES(%s,%s,%s,%s,%s,NOW());"
    val = (exe_result['exe_id'], exe_result['lang'], exe_result['time'], exe_result['memory'], exe_result['code'])
    cursor.execute(sql, val)
    db.commit()  # 数据表有更新时，必须执行这句
    db.close()
