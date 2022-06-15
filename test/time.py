import turtle as tt
import datetime as dt

screen = tt.Screen()
screen.screensize(600, 600)
screen.tracer(0)

pen = tt.Turtle()
pen.hideturtle()
#title = screen.textinput("title", "please input your expected title name")
#screen.title(title)
screen.title("clock")

def draw_circle():
    pen.pencolor("pink")
    pen.up()
    pen.goto(0, -200)
    pen.seth(0)
    pen.down()
    pen.pensize(5)
    pen.circle(200)

    pen.up()
    pen.goto(0, 0)
    pen.seth(90)
    for i in range(12):
        pen.fd(180)
        pen.down()
        pen.fd(20)
        pen.up()
        pen.goto(0, 0)
        pen.rt(6)
        for _ in range(4):
            pen.fd(190)
            pen.down()
            pen.fd(10)
            pen.up()
            pen.goto(0, 0)
            pen.rt(6)


def draw_trick():
    pen.up()
    pen.color("black")
    pen.goto(220, -10)
    pen.write("3", align="center", font=("Arial", 15, "normal"))
    pen.goto(0, 210)
    pen.write("12", align="center", font=("Arial", 15, "normal"))
    pen.goto(-220, -10)
    pen.write("9", align="center", font=("Arial", 15, "normal"))
    pen.goto(0, -235)
    pen.write("6", align="center", font=("Arial", 15, "normal"))


def draw_clockwise(h, m, s):

    pen.up()
    pen.goto(0, 0)
    pen.pencolor("orange")
    pen.down()
    pen.pensize(7)
    pen.seth(90)
    pen.rt(h * 30 + m / 2)
    pen.fd(100)
    arrowhead("orange")

    pen.up()
    pen.goto(0, 0)
    pen.seth(90)
    pen.rt(m * 6 + s / 10)
    pen.pencolor("yellow")
    pen.down()
    pen.pensize(6)
    pen.fd(125)
    arrowhead("yellow")

    pen.up()
    pen.goto(0, 0)
    pen.seth(90)
    pen.rt(s * 6)
    pen.pencolor("green")
    pen.down()
    pen.pensize(5)
    pen.fd(150)
    arrowhead("green")


def arrowhead(color):
    pen.pensize(1)
    pen.up()
    pen.fd(10)
    pen.down()
    pen.color(color)
    pen.begin_fill()
    pen.left(150)
    pen.fd(20)
    pen.left(150)
    pen.fd(10)
    pen.right(60)
    pen.fd(10)
    pen.left(150)
    pen.fd(20)
    pen.end_fill()
    pen.right(30)


while True:
    screen.update()
    now = dt.datetime.now()
    pen.clear()
    draw_circle()
    draw_clockwise(now.hour, now.minute, now.second)
    pen.up()
    pen.goto(0, 230)
    pen.color("blue")
    pen.write("%d:%02d:%02d" % (now.hour, now.minute, now.second), align="center", font=("Arial", 20, "normal"))
    pen.goto(0, -260)
    pen.write("今天是{}年{}月{}日".format(now.year, now.month, now.day), align="center", font=("Arial", 20, "normal"))
    draw_trick()
screen.mainloop()
