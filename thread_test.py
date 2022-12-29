#!env/bin/python

from random import randint
from time import sleep
from threading import Thread

def print_sleep(thread_number):

    sleep_time = randint(1,20)
    print(f'thread {thread_number}: sleeping for{sleep_time}')
    for i in range(sleep_time):
        print(f'thread {thread_number}: {sleep_time-i}...')
        sleep(1)
    print(f'thread {thread_number}: finished')


def blocking_join():
    thread_list = []
    for i in range(10):
        t = Thread(target = print_sleep, args= (i +1,))
        thread_list.append(t)
        t.start()

    for idx, t in enumerate(thread_list):
        t.join()
        print(f'thread {idx+ 1} joined')
    print('main thread done...')



def check_join():
    thread_list = []
    for i in range(10):
        t = Thread(target = print_sleep, args= (i +1,))
        thread_list.append([t, False])
        t.start()

    flag = True
    while flag:
        flag = False
        for idx, t in enumerate(thread_list):
            if t[1]:
                pass
            else:
                if t[0].is_alive():
                    flag = True
                else:
                    t[0].join()
                    t[1] = True
                    print(f'thread {idx+ 1} joined')
    print('main thread done...')
    for t in thread_list:
        print(t[0].name)
    print('\n'*3)
    for e in dir(thread_list[0][0]):
        print(e)


def main():
    check_join()

if __name__ == '__main__':
    print('works')
    main()
