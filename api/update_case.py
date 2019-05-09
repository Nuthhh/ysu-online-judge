#!/usr/bin/python3
# ! -*- coding: utf8 -*-

import os
import mysqlhelper


# 将数据库中的测试用例同步到评测机
def update_testcase(question_id):
    # 获得问题下全部测试用例
    test_list = mysqlhelper.select_question_test_list(question_id)
    path = return_all_path(question_id)
    if os.path.exists(path):
        number = len([lists for lists in os.listdir(path) if os.path.isfile(os.path.join(path, lists))])
        if number == len(test_list) * 2:
            return
        else:
            # 先删除原先旧数据
            filelist = os.listdir(path)
            for f in filelist:
                filepath = os.path.join(path, f)
                if os.path.isfile(filepath):
                    os.remove(filepath)
            # 新建文件
            i = 0
            for test in test_list:
                test_in = test[0]
                f_in = open((path + "%s.in" % i), mode="w", encoding="UTF-8")
                f_in.write(test_in)
                f_in.close()
                test_out = test[1]
                f_out = open((path + "%s.out" % i), mode="w", encoding="UTF-8")
                f_out.write(test_out + '\n')
                f_out.close()
                i = i + 1
    else:
        os.mkdir(path)
        i = 0
        for test in test_list:
            test_in = test[0]
            f_in = open((path + "%s.in" % i), mode="w", encoding="UTF-8")
            f_in.write(test_in)
            f_in.close()
            test_out = test[1]
            f_out = open((path + "%s.out" % i), mode="w", encoding="UTF-8")
            f_out.write(test_out + '\n')
            f_out.close()
            i = i + 1
    return


# 返回测试用例绝对路径
def return_all_path(question_id):
    return "/file/testcase/" + question_id + "/"


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print('Usage:%s srcfile testdata_pth testdata_total')
        exit(-1)
    update_testcase(sys.argv[1])
