import base64
import hashlib
import os
import re
import shutil

from flask import session, make_response
from secrets import token_bytes
from captcha.image import ImageCaptcha
from PIL import Image
from random import choices
from io import BytesIO


# md5加密
def md5(plaintext):
    ciphertext = hashlib.md5()
    ciphertext.update(bytes(plaintext, encoding='utf-8'))
    return ciphertext.hexdigest()


# base64加密
def base64Encoder(plaintext):
    return base64.b64encode(bytes(plaintext, encoding='utf-8'))


# ======== 快排倒叙（由大及小） ========
def quick_sort(array, start, end):
    if start >= end:
        return
    mid_data, left, right = array[start], start, end
    while left < right:
        # while array[right] >= mid_data and left < right:
        while array[right] <= mid_data and left < right:
            right -= 1
        array[left] = array[right]
        # while array[left] < mid_data and left < right:
        while array[left] > mid_data and left < right:
            left += 1
        array[right] = array[left]
    array[left] = mid_data
    quick_sort(array, start, left - 1)
    quick_sort(array, left + 1, end)


# ========


# sql优化
def find_unchinese(file):
    if 'where' in file:
        front_sql = file.strip().split('where')[0]
        pattern = re.compile(r'[\u4e00-\u9fa5]')
        unchinese = str(re.sub(pattern, '', front_sql))
        rep_sql = unchinese.strip().replace('--', '')
        behind_sql = file.strip().split('where')[1]
        to_sql = str(rep_sql + ' where ' + behind_sql)
        return to_sql
    pattern = re.compile(r'[\u4e00-\u9fa5]')
    unchinese = str(re.sub(pattern, '', file))
    rep_sql = unchinese.strip().replace('--', '')
    return rep_sql


# ====== 文件加密 ======
def random_key(length):
    key = token_bytes(nbytes=length)  # 根据指定长度生成随机密钥
    key_int = int.from_bytes(key, 'big')  # 将byte转换为int
    return key_int


def encrypt(raw):  # 加密单元
    raw_bytes = raw.encode()  # 将字符串编码成字节串
    raw_int = int.from_bytes(raw_bytes, 'big')  # 将byte转换成int
    key_int = random_key(len(raw_bytes))  # 根据长度生成密钥
    return raw_int ^ key_int, key_int  # 将密钥与文件异或，返回异或后的结果和密钥


def decrypt(encrypted, key_int):  # 解密单元
    decrypted = encrypted ^ key_int  # 将加密后的文件与密钥异或
    length = (decrypted.bit_length() + 7) // 8  # 计算所占比特大小
    decrypted_bytes = int.to_bytes(decrypted, length, 'big')  # 将int转换回byte
    return decrypted_bytes.decode()


# ========


# ======== 文件移动 ========
def mymovefile(srcfile, dstpath):  # 移动函数
    if not os.path.isfile(srcfile):
        print("%s not exist!" % srcfile)
    else:
        fpath, fname = os.path.split(srcfile)  # 分离文件名和路径
        if not os.path.exists(dstpath):
            os.makedirs(dstpath)  # 创建路径
        shutil.move(srcfile, dstpath + fname)  # 移动文件
        print("move %s -> %s" % (srcfile, dstpath + fname))


# src_dir = '/home/binbao/PycharmProjects/Pro/applications/view/AI/test/'
# dst_dir = '/home/binbao/PycharmProjects/Pro/applications/view/AI/'  # 目的路径记得加斜杠
# ========

# 生成验证码
def get_captcha():
    code, image = gen_captcha()
    out = BytesIO()
    session["code"] = code
    image.save(out, 'png')
    out.seek(0)
    resp = make_response(out.read())
    resp.content_type = 'image/png'
    return resp, code


def gen_captcha(content='2345689abcdefghijklmnpqrstuvwxyzABCDEFGHIJKLMNPQRSTUVWXYZ'):
    """ 生成验证码 """
    image = ImageCaptcha()
    # 获取字符串
    captcha_text = "".join(choices(content, k=4)).lower()
    # 生成图像
    captcha_image = Image.open(image.generate(captcha_text))
    return captcha_text, captcha_image
