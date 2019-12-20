# -*- coding: utf-8 -*-
# !/usr/bin/python3
#
# 本参考脚本用于在服务器端(Windows/Linux主机)接收手势识别模板技能发送的POST数据，
# 严格来说不属于技能模板的一部分，使用前请安装flask
#

from flask import Flask
from flask import request
import json
import base64
import datetime
import time
import pyautogui
import cv2

app = Flask(__name__)
image_path = './images/'
t = 0


def display(action):
    if action == 'up':
        pyautogui.press('up')
    if action == 'down':
        pyautogui.press('down')
    if action == 'en':
        pyautogui.press('enter')


@app.route("/", methods=['POST', 'GET'])
def hello():
    # 接收到的json信息转为dict
    result_dict = json.loads(request.get_data().decode())

    up = result_dict['up']
    down = result_dict['down']
    print('up:', up, ' down:', down)
    if up == 1:
        display('up')
    elif down == 1:
        display('down')

    global t

    # # 提取其中的图片数据并保存到本地
    while time.time() - t > 1:
        t = time.time()
        print(t)
        up_str = result_dict["up_img"]
        down_str = result_dict["down_img"]
        up_image = base64.b64decode(up_str)  # base64解码
        down_image = base64.b64decode(down_str)
        # ori_image.show()
        file_name = str(time.time()) + ".jpg"  # 以当前时间命名
        up_img_file = open(image_path + 'up' + file_name, "wb")
        up_img_file.write(up_image)
        up_img_file.close()
        down_img_file = open(image_path + 'down' + file_name, "wb")
        down_img_file.write(down_image)
        down_img_file.close()

    return "OK"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8088")  # 注意端口号与运行时配置中的保持一致
