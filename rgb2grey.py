import os
import cv2

in_path = '/Users/eveneko/Documents/AI/ModelArts-HiLens/data/rps-cv-images/scissors/'
out_path = '/Users/eveneko/Documents/AI/ModelArts-HiLens/data/rps-cv-images/scissors_l/'


# 顺时针旋转90度
def RotateClockWise90(img):
    trans_img = cv2.transpose(img)
    new_img = cv2.flip(trans_img, 1)
    return new_img


def convert2grey(file):
    img = cv2.imread(in_path + file)
    # img.show()
    L = RotateClockWise90(img)
    L = cv2.cvtColor(L, cv2.COLOR_RGB2GRAY)
    # L.show()
    cv2.imwrite(out_path + file, L)


def main():
    filelist = os.listdir(in_path)
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    for i in filelist:
        if i.split('.')[-1] in {'jpg', 'png'}:
            print(i)
            convert2grey(i)
    print('done')


if __name__ == '__main__':
    main()
