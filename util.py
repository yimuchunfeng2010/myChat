import os


def code_lines_count(path):
    code_lines = 0
    comm_lines = 0
    space_lines = 0
    for root, dirs, files in os.walk(path):
        for item in files:
            file_abs_path = os.path.join(root, item)
            postfix = os.path.splitext(file_abs_path)[1]
            if postfix == '.py':

                with open(file_abs_path, 'rb') as fp:
                    while True:
                        line = fp.readline()
                        if not line:

                            break
                        elif line.strip().startswith(b'#'):

                            comm_lines += 1
                        elif line.strip().startswith(b"'''") or line.strip().startswith(b'"""'):
                            comm_lines += 1
                            if line.count(b'"""') == 1 or line.count(b"'''") == 1:
                                while True:
                                    line = fp.readline()

                                    comm_lines += 1
                                    if ("'''" in line) or ('"""' in line):
                                        break
                        elif line.strip():

                            code_lines += 1
                        else:

                            space_lines += 1

    return code_lines, comm_lines, space_lines


if __name__ == '__main__':
    abs_dir = os.getcwd()
    x, y, z = code_lines_count(abs_dir)
    print("code_lines: ", x)
    print("comm_lines: ", y)
    print("blank_lines: ", z)




# 多线程接受用户输入，并输出打印
# # coding=utf-8
# import threading
# from time import ctime, sleep
#
# mutex = threading.Lock()
#
# msg_arr = ["zeng: haha", "li: zzz", "oo:112"]
#
#
# def say(func):
#     while True:
#         if 0 != len(msg_arr):
#             mutex.acquire(timeout=10)
#             print(msg_arr[0])
#             del msg_arr[0]
#             mutex.release()
#
#
# def listen(func):
#     while True:
#         msg = input()
#         msg = '我说：' + msg
#         # print(msg)
#         mutex.acquire(timeout=10)
#         msg_arr.append(msg)
#         mutex.release()
#
#
#
# threads = []
# t1 = threading.Thread(target=say, args=(u'爱情买卖',))
# threads.append(t1)
# t2 = threading.Thread(target=listen, args=(u'阿凡达',))
# threads.append(t2)
#
# if __name__ == '__main__':
#     # for t in threads:
#     #     t.setDaemon(True)
#     #     t.start()
#     t1.start()
#     t2.start()