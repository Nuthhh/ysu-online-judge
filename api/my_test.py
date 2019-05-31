#!/usr/bin/python3
# ! -*- coding: utf8 -*-

import os
import mysqlhelper
import shutil


# 将学生程序从数据库读取，储存至评测机
# exe_id 学生程序id
# lang 使用的编程语言
# 返回值为程序储存的绝对路径
def save_exe(exe_id, lang):
    lang_map = {1: "Main.java", 2: "Main.cpp"}
    exe_path = '/file/judge/' + exe_id + '/'
    # 为每个程序创建一个目录,在这个目录下只储存一个程序，及其对应的的编译文件
    # 这样的目的是Java程序文件名只能为Main.java，需要使用不同的文件夹进行分离
    context = mysqlhelper.get_exe_info(exe_id)
    exe_file = open((exe_path + lang_map[lang]), mode="w", encoding="UTF-8")
    exe_file.write(context[0])
    exe_file.close()
    return True


print(save_exe('1380784A3F278F7F989A34F8173C0A70', 1))
