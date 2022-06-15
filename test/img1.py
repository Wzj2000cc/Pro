def get_img_stream(img_local_path):
    """
    工具函数:
    获取本地图片流
    :param img_local_path:文件单张图片的本地绝对路径
    :return: 图片流
    """
    import base64
    with open(img_local_path, 'rb') as img_f:
        img_stream = img_f.read()
        img_stream = base64.b64encode(img_stream)
    # return img_stream
    print(img_stream)


img_local_path = '/home/binbao/PycharmProjects/Pro/test/mac1.png'
get_img_stream(img_local_path)
