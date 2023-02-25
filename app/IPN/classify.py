# -*- coding: utf-8 -
import os
import subprocess

root_path = 'd:/desktop/dc'
video_path = 'z_ceshi'
result_path = 'result_path'
resume_path = 'result_path/save_50.pth'


# 只能判断是否执行成功
def os_system(stmt):
    result = os.system(stmt)
    if result is not 0:
        print("命令执行失败")
    else:
        return result  # 结果为0则表示执行成功，为其他值则表示执行不成功


os_system(
    "python main.py --root_path " + root_path + " --video_path " + video_path + " --result_path " + result_path
    + " --resume_path " + resume_path)
# os_system(
#     "python main.py --root_path " + root_path + " --video_path "
#     + video_path + "--result_path " + result_path + " --resume_path " + resume_path)
