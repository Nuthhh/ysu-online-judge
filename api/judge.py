#!/usr/bin/python3
# ! -*- coding: utf8 -*-

import lorun
import os
import mysqlhelper

RESULT_STR = [
    'Accepted',
    'Presentation Error',
    'Time Limit Exceeded',
    'Memory Limit Exceeded',
    'Wrong Answer',
    'Runtime Error',
    'Output Limit Exceeded',
    'Compile Error',
    'System Error'
]


# exe_name 学生提交程序名称，因为学生提交程序的路径固定，所以只需传值程序名称
# lang 1 java 2 c++
def compileSrc(exe_name, lang):
    if lang == 1:
        print("未支持当前语言")
        return False
    elif lang == 2:
        if os.system('g++ /file/test/%s -o %s' % (exe_name, exe_name[:exe_name.index(".")])) != 0:
            return False
    return True


# exe_name 编译后的程序名称
# in_path 测试用例输入
# out_path 测试用例输出
# time 题目运行时间限制
# memory 题目运行内存限制
def runone(exe_name, in_path, out_path, time, memory):
    out = exe_name + ".out"
    fin = open(in_path)
    ftemp = open(out, 'w')

    runcfg = {
        'args': ['./' + exe_name],
        'fd_in': fin.fileno(),
        'fd_out': ftemp.fileno(),
        'timelimit': time,  # in MS
        'memorylimit': memory,  # in KB
    }

    rst = lorun.run(runcfg)
    fin.close()
    ftemp.close()

    if rst['result'] == 0:
        ftemp = open(out)
        fout = open(out_path)
        crst = lorun.check(fout.fileno(), ftemp.fileno())
        fout.close()
        ftemp.close()
        os.remove(out)
        if crst != 0:
            return {'result': crst}

    return rst


# 返回测试用例绝对路径
def return_all_path(question_id):
    return "/file/testcase/" + question_id + "/"


# exe_id 学生提交程序id
# exe_name 学生提交程序在评测机的名称
# question_id 作答题目id
# lang 学生提交程序使用的语言 1Java 2C++
def judge(exe_id, exe_name, question_id, lang):
    # 用于储存结果
    result = {'exe_id': exe_id, 'lang': lang, 'time': 0, 'memory': 0, 'code': 8}
    if not compileSrc(exe_name, lang):
        result['code'] = 7
        mysqlhelper.insert_exe_result(result)
        return
    # 将数据库中测试用例同步到评测机，返回值为总测试用例数
    td_total = len(mysqlhelper.select_question_test_list(question_id))
    path = return_all_path(question_id)
    # 题目名称前缀 Main.cpp Main
    exe_name_pre = exe_name[:exe_name.index(".")]
    # 下面获得题目运行时间和运行内存要求
    question = mysqlhelper.get_question_info(question_id)
    question_time, question_memory = 0, 0
    if lang == 1:
        question_time = question[0] * 2
        question_memory = question[1] * 2
    elif lang == 2:
        question_time = question[0]
        question_memory = question[1]
    # 运行测试用例
    for i in range(td_total):
        in_path = os.path.join(path, '%d.in' % i)
        out_path = os.path.join(path, '%d.out' % i)
        if os.path.isfile(in_path) and os.path.isfile(out_path):
            rst = runone(exe_name_pre, in_path, out_path, question_time, question_memory)
            result['code'] = rst['result']
            if rst['result'] != 0:
                mysqlhelper.insert_exe_result(result)
                return
            if rst['memoryused'] > result['memory']:
                result['memory'] = rst['memoryused']
            if rst['timeused'] > result['time']:
                result['time'] = rst['timeused']
        else:
            result['code'] = 8
            os.remove('./%s' % exe_name_pre)
            exit(-1)
    os.remove('./%s' % exe_name_pre)
    mysqlhelper.insert_exe_result(result)


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 5:
        print('Usage:%s srcfile testdata_pth testdata_total')
        exit(-1)
    judge(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]))
