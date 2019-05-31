#!/usr/bin/python3
# ! -*- coding: utf8 -*-

import lorun
import os
import mysqlhelper
import shutil
import shlex

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


# 返回程序路径
def return_exe_all_path(exe_id, lang):
    lang_map = {1: "Main.java", 2: "Main.cpp"}
    return '/file/judge/' + exe_id + '/' + lang_map[lang]


# 返回程序的目录
def return_exe_path(exe_id):
    return '/file/judge/' + exe_id + '/'


# 返回题目对应的测试用例目录
def return_testcase_path(question_id):
    return "/file/testcase/" + question_id + "/"


# 将学生程序从数据库读取，储存至评测机
# exe_id 学生程序id
# lang 使用的编程语言
# 返回值为程序储存的绝对路径
def save_exe(exe_id, lang):
    exe_path = return_exe_path(exe_id)
    exe_all_path = return_exe_all_path(exe_id, lang)
    # 为每个程序创建一个目录,在这个目录下只储存一个程序，及其对应的的编译文件
    # 这样的目的是Java程序文件名只能为Main.java，需要使用不同的文件夹进行分离
    if os.path.exists(exe_path):
        shutil.rmtree(exe_path)
    os.mkdir(exe_path)
    context = mysqlhelper.get_exe_info(exe_id)
    exe_file = open(exe_all_path, mode="w", encoding="UTF-8")
    exe_file.write(context[0])
    exe_file.close()
    return True


# exe_name 学生提交程序名称，因为学生提交程序的路径固定，所以只需传值程序名称
# lang 1 java 2 c++
def compileSrc(lang, exe_id):
    if lang == 1:
        if os.system('javac -d %s %s' % (return_exe_path(exe_id), return_exe_all_path(exe_id, lang))) != 0:
            return False
    elif lang == 2:
        if os.system('g++ %s -o %s' % (return_exe_all_path(exe_id, lang), exe_id)) != 0:
            return False
    return True


# exe_name 编译后的程序名称
# in_path 测试用例输入
# out_path 测试用例输出
# time 题目运行时间限制
# memory 题目运行内存限制
def run_one(exe_id, lang, in_path, out_path, time, memory):
    out = exe_id + ".out"
    fin = open(in_path)
    ftemp = open(out, 'w')
    run_map = {1: "java -cp " + return_exe_path(exe_id) + " Main", 2: "./" + exe_id}
    main_exe = shlex.split(run_map[lang])
    print(main_exe)
    run_config = {
        'args': main_exe,
        'fd_in': fin.fileno(),
        'fd_out': ftemp.fileno(),
        'timelimit': time,  # in MS
        'memorylimit': memory,  # in KB
    }

    rst = lorun.run(run_config)
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


# exe_id 学生提交程序id
# exe_name 学生提交程序在评测机的名称
# question_id 作答题目id
# lang 学生提交程序使用的语言 1Java 2C++
def judge(exe_id, question_id, lang):
    # 用于储存结果
    result = {'exe_id': exe_id, 'lang': lang, 'time': 0, 'memory': 0, 'code': 8}

    # 提取学生程序
    save_exe(exe_id, lang)

    # 编译程序
    if not compileSrc(lang, exe_id):
        result['code'] = 7
        mysqlhelper.insert_exe_result(result)
        return

    # 题目名称前缀 Main.cpp Main
    # exe_name_pre = exe_name[:exe_name.index(".")]

    # 下面获得题目运行时间和运行内存要求
    question = mysqlhelper.get_question_info(question_id)
    question_time, question_memory = 0, 0
    if lang == 1:
        question_time = question[0] * 2
        question_memory = question[1] * 2
    elif lang == 2:
        question_time = question[0]
        question_memory = question[1]

    # 将数据库中测试用例同步到评测机，返回值为总测试用例数
    td_total = len(mysqlhelper.select_question_test_list(question_id))
    # 获得题目对应的测试用例路径
    path = return_testcase_path(question_id)
    # 运行测试用例
    for i in range(td_total):
        in_path = os.path.join(path, '%d.in' % i)
        out_path = os.path.join(path, '%d.out' % i)
        if os.path.isfile(in_path) and os.path.isfile(out_path):
            rst = run_one(exe_id, lang, in_path, out_path, question_time, question_memory)
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
            if lang == 2:
                os.remove('./%s' % exe_id)
            mysqlhelper.insert_exe_result(result)
            exit(-1)
    if lang == 2:
        os.remove('./%s' % exe_id)
    mysqlhelper.insert_exe_result(result)


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 4:
        print('Usage:%s srcfile testdata_pth testdata_total')
        exit(-1)
    judge(sys.argv[1], sys.argv[2], int(sys.argv[3]))
