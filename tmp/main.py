#! /usr/bin/python3.7
# 使用前请配置如下运行时配置项：
# server_url ：用于接收POST数据，形如 http://192.168.123.11:8088

import hilens
from old.utils import *


def run():
    # 配置系统日志级别
    hilens.set_log_level(hilens.ERROR)

    # 系统初始化，参数要与创建技能时填写的检验值保持一致
    hilens.init("gesture")

    # 初始化模型
    gesture_model_path = hilens.get_model_dir() + "model.om"
    gesture_model = hilens.Model(gesture_model_path)

    # 初始化本地摄像头与HDMI显示器
    camera = hilens.VideoCapture()
    display_hdmi = hilens.Display(hilens.HDMI)

    # img_w = hilens.VideoCapture.width
    # img_h = hilens.VideoCapture.height
    # print('hilens.VideoCapture.width: ', hilens.VideoCapture.width)
    # print('hilens.VideoCapture.height: ', hilens.VideoCapture.height)

    # 上一次上传OBS图片的时间与上传间隔
    last_upload_time = 0
    upload_duration = 5

    # 读取技能配置
    skill_cfg = hilens.get_skill_config()
    if skill_cfg is None or 'server_url' not in skill_cfg:
        hilens.error("server_url not configured")
        return

    while True:
        # 读取一帧图片(YUV NV21格式)
        input_yuv = camera.read()

        # 图片预处理：转为RGB格式、缩放为模型输入尺寸
        img_rgb1 = cv2.cvtColor(input_yuv, cv2.COLOR_YUV2RGB_NV21)
        img_rgb2 = img_rgb1.copy()
        input_img = img_rgb1.copy()
        img_preprocess, img_w, img_h = preprocess(input_img)
        # input1 = hilens.Preprocessor.crop(img_rgb1, 0, 0, int(img_w / 2) * 2, int(img_h / 4) * 2, 1)
        # input2 = hilens.Preprocessor.crop(img_rgb2, 0, int(img_h / 4) * 2, int(img_w / 2) * 2, int(img_h / 2) * 2, 1)

        # 模型推理
        output = gesture_model.infer([input_img.flatten()])
        # output1 = gesture_model.infer([input1.flatten()])
        # output2 = gesture_model.infer([input2.flatten()])

        # 后处理得到手势所在区域与类别，并在RGB图中画框
        bboxes = get_result(output, img_w, img_h)
        input_img = draw_boxes(input_img, bboxes)

        # 输出处理后的图像到HDMI显示器，必须先转回YUV NV21格式
        output_yuv = hilens.cvt_color(input_img, hilens.RGB2YUV_NV21)
        display_hdmi.show(output_yuv)

        # 上传OK手势图片到OBS，为防止OBS数据存储过多，间隔一定的时间才上传图片
        # if time.time() - last_upload_time > upload_duration:
        #     # 截取出OK手势图片(如果有的话)
        #     img_OK = get_OK(img_rgb, bboxes)
        #     if img_OK is not None:
        #         # 上传OK手势图片到OBS，图片(用当前时间命名)需要先转为BGR格式并按照jpg格式编码
        #         img_OK = cv2.cvtColor(img_OK, cv2.COLOR_RGB2BGR)
        #         img_OK = cv2.imencode('.jpg', img_OK)[1]
        #         filename = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        #         ret = hilens.upload_bufer(filename + "_OK.jpg", img_OK, "write")
        #         if ret != 0:
        #             hilens.error("upload pic failed!")
        #             return
        #
        #         last_upload_time = time.time()
        #
        # 以POST方式传输处理后的整张图片
        try:
            post_msg(skill_cfg['server_url'], input_img)
        except Exception as e:
            hilens.error("post data failed!")
            print("Reason : ", e)

    hilens.terminate()


if __name__ == "__main__":
    run()
