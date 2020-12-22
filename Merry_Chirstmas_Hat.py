# Summary:   戴圣诞帽
# Author:       LiuXiaolong, Amusi
# Date:           2017-12-25
# Reference:  http://cvmart.net/community/article/detail/168
# Reference:  https://github.com/LiuXiaolong19920720/Add-Christmas-Hat
# Note:          参考LiuXiaoLong核心代码add_hat，添加视频读取帧代码
# Library:     Python + Dlib + OpenCV(本人使用Python3.6+Dlib19.8+OpenCV3.3)

# Updated: Python 实用宝典
# https://pythondict.com


import cv2
import dlib

# 给img中的人头像加上圣诞帽，人脸最好为正脸


def add_hat(img, hat_img):
    # 分离rgba通道，合成rgb三通道帽子图，a通道后面做mask用
    r, g, b, a = cv2.split(hat_img)
    rgb_hat = cv2.merge((r, g, b))

    # 保存帽子的aplph通道图像
    cv2.imwrite("hat_alpha.jpg", a)

    # ------------------------- dlib人脸检测-----------------------
    # dlib人脸关键点检测器(需要确保.py文件同级目录下有shape_predictor_5_face_landmarks.dat这个文件)
    predictor_path = "shape_predictor_5_face_landmarks.dat"
    predictor = dlib.shape_predictor(predictor_path)

    # dlib正脸检测器
    detector = dlib.get_frontal_face_detector()

    # 正脸检测
    dets = detector(img, 1)

    # 如果检测到人脸
    if len(dets) > 0:
        # 遍历所有人脸
        for d in dets:
            x, y, w, h = d.left(), d.top(), d.right()-d.left(), d.bottom()-d.top()

            # 关键点检测，5个关键点
            shape = predictor(img, d)

            # 选取左(0)右(2)眼眼角的点
            point1 = shape.part(0)
            point2 = shape.part(2)

            # 求两点中心
            eyes_center = ((point1.x+point2.x)//2, (point1.y+point2.y)//2)

            #  根据人脸大小调整帽子大小
            factor = 1.5    # 比例因子
            resized_hat_h = int(
                round(rgb_hat.shape[0]*w/rgb_hat.shape[1]*factor))
            resized_hat_w = int(
                round(rgb_hat.shape[1]*w/rgb_hat.shape[1]*factor))

            # 避免帽子高度超出图像画面
            if resized_hat_h > y:
                resized_hat_h = y-1

            # 根据人脸大小调整帽子大小
            resized_hat = cv2.resize(rgb_hat, (resized_hat_w, resized_hat_h))

            # 用alpha通道作为mask(bitwise_not)
            mask = cv2.resize(a, (resized_hat_w, resized_hat_h))
            mask_inv = cv2.bitwise_not(mask)

            # 帽子相对与人脸框上线的偏移量
            dh = 0
            dw = 0

            # 原图ROI
            bg_roi = img[y+dh-resized_hat_h:y+dh,
                         (eyes_center[0]-resized_hat_w//3):(eyes_center[0]+resized_hat_w//3*2)]

            # 原图ROI中提取放帽子的区域
            bg_roi = bg_roi.astype(float)
            mask_inv = cv2.merge((mask_inv, mask_inv, mask_inv))
            alpha = mask_inv.astype(float)/255

            # 相乘之前保证两者大小一致（可能会由于四舍五入原因不一致）
            alpha = cv2.resize(alpha, (bg_roi.shape[1], bg_roi.shape[0]))
            bg = cv2.multiply(alpha, bg_roi)
            bg = bg.astype('uint8')

            cv2.imwrite("bg.jpg", bg)

            # 提取帽子区域
            hat = cv2.bitwise_and(resized_hat, resized_hat, mask=mask)
            cv2.imwrite("hat.jpg", hat)

            # 相加之前保证两者大小一致（可能会由于四舍五入原因不一致）
            hat = cv2.resize(hat, (bg_roi.shape[1], bg_roi.shape[0]))
            # 两个ROI区域相加
            add_hat = cv2.add(bg, hat)

            # 把添加好帽子的区域放回原图
            img[y+dh-resized_hat_h:y+dh, (eyes_center[0]-resized_hat_w//3):(
                eyes_center[0]+resized_hat_w//3*2)] = add_hat

            return 1, img
    else:
        print("没有检测到正脸，请检查输入图像!")
        return -1, img


def method_one():
    """
    方式1: 打开摄像头读取头像图
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print('摄像头打开失败!')
    else:
        print('摄像头打开成功!')
        print("请按下键盘上的'q'，保存当前满意图像!")
        while cap.isOpened():
            _, img = cap.read()
            cv2.imshow("img", img)
            k = cv2.waitKey(33) & 0xFF
            if(k == ord('q')):
                cv2.imwrite("sefile.jpg", img)
                face_flag, output = add_hat(img, hat_img)
                if(-1 == face_flag):
                    break
                cv2.imshow("output", output)
                print("请按下键盘上的任意按键，退出当前程序!")
                cv2.waitKey(0)
                cv2.imwrite("output.jpg", output)
                break


def method_two(hat_img, filename):
    """
    方式2: 从本地读取一幅头像图
    """
    img = cv2.imread(filename)
    success, output = add_hat(img, hat_img)
    if not success:
        print("戴失败了！")
        return
    # 展示效果
    cv2.imshow("output", output)
    cv2.waitKey(0)
    cv2.imwrite("output.jpg", output)


def method_three(hat_img):
    """
    方式3: 从文件夹中读取多福头像图（批量处理）
    """
    import glob as gb

    img_path = gb.glob("./images/*.jpg")

    for path in img_path:
        img = cv2.imread(path)

        # 添加帽子
        success, output = add_hat(img, hat_img)
        if not success:
            print("戴失败了！")
            return

        # 展示效果
        cv2.imshow("output", output)
        cv2.waitKey(0)


# 读取帽子图，第二个参数-1表示读取为rgba通道，否则为rgb通道
hat_img = cv2.imread("hat.png", -1)

# 选择你需要的方式
method_two(hat_img, "test.jpg")

cv2.destroyAllWindows()
