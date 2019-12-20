# -*- coding: utf-8 -*-
# ! /usr/bin/python3.7
import hilens
import cv2
import numpy as np
import json
import base64
# 安装在Hilens上：python3 -m pip install requests
import requests

labels = ["Paper", "Rock"]
score_thres = 0.7
frame_size = [1280, 720]


def softmax(x):
    x = x - np.max(x, axis=0)
    ex = np.exp(x)
    return ex/np.sum(ex, axis=0)


# 以POST方式传输检测结果
def post_msg(server_url, up, down, up_img, down_img):
    # img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    up_str = cv2.imencode('.jpg', up_img)[1].tostring()
    up_bin = base64.b64encode(up_str)
    down_str = cv2.imencode('.jpg', down_img)[1].tostring()
    down_bin = base64.b64encode(down_str)
    # post_data = {'up': up_bin.decode('utf-8'),
    #              'down': down_bin.decode('utf-8')
    #              }
    post_data = {'up': up,
                 'down': down,
                 'up_img': up_bin.decode('utf-8'),
                 'down_img': down_bin.decode('utf-8')
                 }
    print(post_data)
    ret = requests.post(server_url, json.dumps(post_data).encode('utf-8'))
    return ret


def run():
    hilens.set_log_level(hilens.INFO)

    # 构造摄像头
    cap = hilens.VideoCapture()
    disp = hilens.Display(hilens.HDMI)

    hilens.info("Hilens camera init successful!")

    # 模型初始化
    gesture_model_path = hilens.get_model_dir() + "model.om"
    gesture_model = hilens.Model(gesture_model_path)

    hilens.info("AirGesture model init successful!")

    # 读取技能配置
    skill_cfg = hilens.get_skill_config()
    if skill_cfg is None or 'server_url' not in skill_cfg:
        skill_cfg = {"server_url": "http://192.168.2.2:8088"}
        # hilens.error("server_url not configured")
        # return

    while True:
        # 获取一帧画面
        frame = cap.read()

        # 使用opencv进行转换
        bgr = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR_NV21)
        rgb = cv2.cvtColor(frame, cv2.COLOR_YUV2RGB_NV21)
        grey = cv2.cvtColor(frame, cv2.COLOR_YUV2GRAY_NV21)
        input_resized = cv2.cvtColor(grey, cv2.COLOR_GRAY2RGB)
        up = input_resized[int(frame_size[1] / 2 - 300):int(frame_size[1] / 2 + 300), int(frame_size[0] / 4 - 200):int(frame_size[0] / 4 + 200)]
        down = input_resized[int(frame_size[1] / 2 - 300):int(frame_size[1] / 2 + 300), int(frame_size[0] * 3 / 4 - 200):int(frame_size[0] * 3 / 4 + 200)]
        up_resized = cv2.resize(up, (200, 300))
        down_resized = cv2.resize(down, (200, 300))

        # 推理
        up_p = 0
        down_p = 0

        up_output = gesture_model.infer([up_resized.astype(np.float32).flatten()])
        predict = softmax(up_output[0])
        max_inx = np.argmax(predict)

        if predict[max_inx] > score_thres:
            text = labels[max_inx]
            if text == 'Paper':
                up_p = 1
            else:
                up_p = 0
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 4
            thickness = 8
            color = (0, 0, 0)
            size = cv2.getTextSize(text, font, font_scale, thickness)
            text_width = size[0][0]
            text_height = size[0][1]
            cv2.putText(rgb, text,
                        (int((frame_size[0] / 2 - text_width) / 2), frame_size[1] - 2 * int(text_height)),
                        font, font_scale, color, thickness)

        down_output = gesture_model.infer([down_resized.astype(np.float32).flatten()])
        predict = softmax(down_output[0])
        max_inx = np.argmax(predict)

        if predict[max_inx] > score_thres:
            text = labels[max_inx]
            if text == 'Paper':
                down_p = 1
            else:
                down_p = 0
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 4
            thickness = 8
            color = (0, 0, 0)
            size = cv2.getTextSize(text, font, font_scale, thickness)
            text_width = size[0][0]
            text_height = size[0][1]
            cv2.putText(rgb, text,
                        (int((frame_size[0] * 3 / 2 - text_width) / 2), frame_size[1] - 2 * int(text_height)),
                        font, font_scale, color, thickness)

        # 以POST方式传输处理后的整张图片
        try:
            post_msg(skill_cfg['server_url'], up_p, down_p, up_resized, down_resized)
        except Exception as e:
            hilens.error("Post data failed!")
            print("Reason : ", e)

        text = 'UP'
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 4
        thickness = 8
        color = (228, 31, 43)
        size = cv2.getTextSize(text, font, font_scale, thickness)
        text_width = size[0][0]
        text_height = size[0][1]
        cv2.putText(rgb, text, (int((frame_size[0] * 1 / 2 - text_width) / 2), int((frame_size[1] - text_height) / 2)),
                    font, font_scale, color, thickness)

        text = 'DOWN'
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 4
        thickness = 8
        color = (228, 31, 43)
        size = cv2.getTextSize(text, font, font_scale, thickness)
        text_width = size[0][0]
        text_height = size[0][1]
        cv2.putText(rgb, text, (int((frame_size[0] * 3 / 2 - text_width) / 2), int((frame_size[1] - text_height) / 2))
                    , font, font_scale, color, thickness)

        cv2.rectangle(rgb, (int(frame_size[0] / 4 - 200), int(frame_size[1] / 2 - 300)), (int(frame_size[0] / 4 + 200), int(frame_size[1] / 2 + 300)), (255, 255, 0), 8)
        cv2.rectangle(rgb, (int(frame_size[0] * 3 / 4 - 200), int(frame_size[1] / 2 - 300)), (int(frame_size[0] * 3 / 4 + 200), int(frame_size[1] / 2 + 300)), (255, 255, 0), 8)

        cv2.line(rgb, (frame_size[0] // 2, 0), (frame_size[0] // 2, frame_size[1]), (255, 255, 255), 8)
        cv2.line(rgb, (0, 0), (frame_size[0], 0), (255, 255, 255), 16)
        cv2.line(rgb, (0, 0), (0, frame_size[1]), (255, 255, 255), 16)
        cv2.line(rgb, (frame_size[0], 0), (frame_size[0], frame_size[1]), (255, 255, 255), 16)
        cv2.line(rgb, (0, frame_size[1]), (frame_size[0], frame_size[1]), (255, 255, 255), 16)

        # 使用hilens进行颜色转换
        nv21 = hilens.cvt_color(rgb, hilens.RGB2YUV_NV21)

        # 输出到HDMIs
        disp.show(nv21)


if __name__ == '__main__':
    hilens.init("gesture")
    run()
    hilens.terminate()
