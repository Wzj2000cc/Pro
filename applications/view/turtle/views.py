import json
from datetime import datetime

from flask import Blueprint, request, Response
from common.utils import ck_login, validate, logs
from common.utils.http import success_api, fail_api

Turtle_blu = Blueprint('tur', __name__)
algorithm_dict = {"冒泡排序": "bubbleSort", "选择排序": "selectionSort", "插入排序": "insertionSort", "希尔排序": "shellSort",
                  "归并排序": "mergeSort", "快速排序": "quickSort", "计数排序": "counting_sort"}


class Algorithm(object):

    # 冒泡排序
    def bubbleSort(self, arr):
        for i in range(1, len(arr)):
            exchange = False
            for j in range(0, len(arr) - i):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
            if not exchange:
                return arr
        return arr

    # 选择排序
    def selectionSort(self, arr):
        for i in range(len(arr) - 1):
            # 记录最小数的索引
            minIndex = i
            for j in range(i + 1, len(arr)):
                if arr[j] < arr[minIndex]:
                    minIndex = j
            # i 不是最小数时，将 i 和最小数进行交换
            if i != minIndex:
                arr[i], arr[minIndex] = arr[minIndex], arr[i]
        return arr

    # 插入排序
    def insertionSort(self, arr):
        for i in range(len(arr)):
            preIndex = i - 1
            current = arr[i]
            while preIndex >= 0 and arr[preIndex] > current:
                arr[preIndex + 1] = arr[preIndex]
                preIndex -= 1
            arr[preIndex + 1] = current
        return arr

    # 希尔排序
    def shellSort(self, arr):
        import math
        gap = 1
        while (gap < len(arr) / 3):
            gap = gap * 3 + 1
        while gap > 0:
            for i in range(gap, len(arr)):
                temp = arr[i]
                j = i - gap
                while j >= 0 and arr[j] > temp:
                    arr[j + gap] = arr[j]
                    j -= gap
                arr[j + gap] = temp
            gap = math.floor(gap / 3)
        return arr

    # 归并排序
    def mergeSort(self, arr):
        import math
        if (len(arr) < 2):
            return arr
        middle = math.floor(len(arr) / 2)
        left, right = arr[0:middle], arr[middle:]
        return self.merge(self.mergeSort(left), self.mergeSort(right))

    def merge(self, left, right):
        result = []
        while left and right:
            if left[0] <= right[0]:
                result.append(left.pop(0))
            else:
                result.append(right.pop(0))
        while left:
            result.append(left.pop(0))
        while right:
            result.append(right.pop(0))
        return result

    # 快速排序
    def quickSort(self, arr, left=None, right=None):
        left = 0 if not isinstance(left, (int, float)) else left
        right = len(arr) - 1 if not isinstance(right, (int, float)) else right
        if left < right:
            partitionIndex = self.partition(arr, left, right)
            self.quickSort(arr, left, partitionIndex - 1)
            self.quickSort(arr, partitionIndex + 1, right)
        return arr

    def partition(self, arr, left, right):
        pivot = left
        index = pivot + 1
        i = index
        while i <= right:
            if arr[i] < arr[pivot]:
                self.swap(arr, i, index)
                index += 1
            i += 1
        self.swap(arr, pivot, index - 1)
        return index - 1

    def swap(self, arr, i, j):
        arr[i], arr[j] = arr[j], arr[i]

    # 计数排序
    def counting_sort(self, array):
        if len(array) < 2:
            return array
        max_num = max(array)
        count = [0] * (max_num + 1)
        for num in array:
            count[num] += 1
        new_array = list()
        for i in range(len(count)):
            for j in range(count[i]):
                new_array.append(i)
        return new_array


# ================= 堆排序 ========================
def buildMaxHeap(arr):
    import math
    for i in range(math.floor(len(arr) / 2), -1, -1):
        heapify(arr, i)


def heapify(arr, i):
    left = 2 * i + 1
    right = 2 * i + 2
    largest = i
    if left < arrLen and arr[left] > arr[largest]:
        largest = left
    if right < arrLen and arr[right] > arr[largest]:
        largest = right

    if largest != i:
        swap(arr, i, largest)
        heapify(arr, largest)


def swap(arr, i, j):
    arr[i], arr[j] = arr[j], arr[i]


def heapSort(arr):
    global arrLen
    arrLen = len(arr)
    buildMaxHeap(arr)
    for i in range(len(arr) - 1, 0, -1):
        swap(arr, 0, i)
        arrLen -= 1
        heapify(arr, 0)
    return arr


# ================= 二分查找 =======================
def two_search(l, aim, start=0, end=None):
    end = len(l) - 1 if end is None else end
    mid_index = (end - start) // 2 + start
    if end >= start:
        if aim > l[mid_index]:
            return two_search(l, aim, start=mid_index + 1, end=end)

        elif aim < l[mid_index]:
            return two_search(l, aim, start=start, end=mid_index - 1)

        elif aim == l[mid_index]:
            return mid_index
        else:
            return '没有此值'
    else:
        return '没有此值'


@Turtle_blu.route('/alg', methods=['POST'])
def algorithm():
    data = request.get_data()
    json_data = json.loads(data)
    uname = validate.xss_escape(json_data.get('uname'))
    sort_name = validate.xss_escape(json_data.get('sort_name'))
    user_list = list(json_data.get('num_list'))
    num_list = user_list[:]

    # ======== 安全登录校验 ========
    if ck_login.is_status(uname) is None:
        return fail_api(msg='该用户不存在，请注册或换账号登录！')
    if not ck_login.is_status(uname):
        return fail_api(msg='当前状态为离线，请重新登录！')
    if not uname:
        return fail_api(msg='用户名输入为空，请重新输入')
    # ================

    alg_obj = Algorithm()
    start = datetime.now()

    result = None
    if sort_name == '堆排序':
        result = heapSort(num_list)
    else:
        try:
            a_method = algorithm_dict[sort_name]
            result = getattr(Algorithm, a_method)(alg_obj, num_list)
        except Exception as e:
            print(e)
    end = datetime.now()

    logs.logger.info(f'用户（{uname}）使用（{sort_name}）计算了数列（{user_list}）\n'
                     f'耗时（{end - start}）\n'
                     f'计算结果为（{result}）')
    return success_api(f'用户（{uname}）使用（{sort_name}）计算了数列（{user_list}）\n'
                       f'耗时（{end - start}）\n'
                       f'计算结果为（{result}）')


# ================= 二分查找算法 ========================
@Turtle_blu.route('/alg2', methods=['POST'])
def algorithm_two():
    data = request.get_data()
    json_data = json.loads(data)
    uname = validate.xss_escape(json_data.get('uname'))
    num_list = list(json_data.get('num_list'))
    find_num = int(json_data.get('find_num'))

    # ======== 安全登录校验 ========
    if ck_login.is_status(uname) is None:
        return fail_api(msg='该用户不存在，请注册或换账号登录！')
    if not ck_login.is_status(uname):
        return fail_api(msg='当前状态为离线，请重新登录！')
    if not uname:
        return fail_api(msg='用户名输入为空，请重新输入')
    # ================

    result = two_search(num_list, find_num)

    logs.logger.info(f'用户（{uname}）提供的数列为：{num_list}, '
                     f'使用（二分查找算法）查找的数字（{find_num}）位于第（{int(result) + 1}）位')
    return success_api(f'用户（{uname}）提供的数列为：{num_list} \n'
                       f'使用（二分查找算法）查找的数字（{find_num}）位于第（{int(result) + 1}）位')
