from application.apps.auth.models import User

from tkinter import *
from tkinter import messagebox
import tkinter as tk
win = Tk()
win.title('国家电网平台内网登录系统')
win.geometry('400x200')
win.resizable(0, 0)

Label(text='账号：').place(x=80, y=30)
uname = Entry(win)
uname.place(x=130, y=30)

Label(text='密码：').place(x=80, y=70)
pwd = Entry(win)
pwd.place(x=130, y=70)


def login():
    username = uname.get()
    password = pwd.get()
    user = User.query.filter_by(uname=username).all()
    mima = User.query.filter_by(pwd=password).all()
    if user and mima:
        if messagebox.askokcancel('Quit', '登陆成功，点击退出'):
            win.destroy()
    elif username == '' or password == '':
        messagebox.askokcancel('Quit', '账号或密码为空，请重新输入')
    else:
        messagebox.askokcancel('Quit', '账号或密码错误，请重新输入')


def out():
    if messagebox.askokcancel('Quit', 'Do you want to quit?'):
        win.destroy()


Button(text='登录', command=login).place(x=150, y=110)
Button(text='退出', command=out).place(x=210, y=110)

win.mainloop()
