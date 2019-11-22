# Elegant Chaos Pt2 (Chapter 6)
# revision 2
# Daniel W. Grace

import sys
import math
import time
import threading
from tkinter import *

# Runge Kutta method in 4 dimensions
def rK4(a, b, c, d, fa, fb, fc, fd, s):
	a1 = fa(a, b, c, d)*s
	b1 = fb(a, b, c, d)*s
	c1 = fc(a, b, c, d)*s
	d1 = fd(a, b, c, d)*s
	ak = a + a1*0.5
	bk = b + b1*0.5
	ck = c + c1*0.5
	dk = d + d1*0.5
	a2 = fa(ak, bk, ck, dk)*s
	b2 = fb(ak, bk, ck, dk)*s
	c2 = fc(ak, bk, ck, dk)*s
	d2 = fd(ak, bk, ck, dk)*s
	ak = a + a2*0.5
	bk = b + b2*0.5
	ck = c + c2*0.5
	dk = d + d2*0.5
	a3 = fa(ak, bk, ck, dk)*s
	b3 = fb(ak, bk, ck, dk)*s
	c3 = fc(ak, bk, ck, dk)*s
	d3 = fd(ak, bk, ck, dk)*s
	ak = a + a3
	bk = b + b3
	ck = c + c3
	dk = d + d3
	a4 = fa(ak, bk, ck, dk)*s
	b4 = fb(ak, bk, ck, dk)*s
	c4 = fc(ak, bk, ck, dk)*s
	d4 = fd(ak, bk, ck, dk)*s
	a = a + (a1 + 2*(a2 + a3) + a4)/6
	b = b + (b1 + 2*(b2 + b3) + b4)/6
	c = c + (c1 + 2*(c2 + c3) + c4)/6
	d = d + (d1 + 2*(d2 + d3) + d4)/6
	return a, b, c, d

# supporting classes / functions
class Graph:
    def __init__(self, x0, sx, y0, sy):
        self.x0 = x0
        self.sx = sx
        self.y0 = y0
        self.sy = sy

def line(canvas, g, p, i, xp, yp, xq, yq):
    x0 = int((xp + g.x0) * g.sx)
    y0 = int((yp + g.y0) * g.sy)
    x1 = int((xq + g.x0) * g.sx)
    y1 = int((yq + g.y0) * g.sy)
    canvas.create_line(x0, y0, x1, y1, fill=p.col(i))

class Color:
    def __init__(self, r, g, b):
        self.red = r
        self.gre = g
        self.blu = b
    def hexVal(self, v):
        return (hex(v)[2:]).zfill(2)
    def str(self):
        return "#" + self.hexVal(self.red) + self.hexVal(self.gre) + self.hexVal(self.blu)
    
class Palette:
    def __init__(self, n0, p):
        self.colors = []
        self.n = n0
        self.m = 0
        if p == "std":
            self.std()
    def add(self, c):
        self.colors.append(c)
        self.m += 1
    def std(self):
        self.add(Color(0, 191, 127))
        self.add(Color(191, 127, 0))
        self.add(Color(127, 0, 191))
    def col(self, i):
        k = i % (self.n*self.m)
        z = k // self.n
        j = k % self.n
        c0 = self.colors[z]
        c1 = self.colors[(z + 1) % self.m]
        t0 = (self.n - j)/self.n
        t1 = j/self.n
        r = int(math.floor(c0.red*t0 + c1.red*t1)) 
        g = int(math.floor(c0.gre*t0 + c1.gre*t1)) 
        b = int(math.floor(c0.blu*t0 + c1.blu*t1)) 
        c = Color(r, g, b)
        return c.str()

class TaskLock:
    def __init__(self):
        self.t = None
        self.k = threading.Lock()
    def set(self, t0):
        with self.k:
            self.t = t0
    
def tryLine(canvas, g, p, i, xp, vp, xq, vq, d):
    try:
        line(canvas, g, p, i, xp, vp, xq, vq)
        if i % d == 0:
            upd(canvas)
        return True
    except TclError:
        return False

def upd(canvas):
    try:
        canvas.update()
        return True
    except TclError:
        return False

def v4Fx(v, w, x, y):
    return v

def w4Fy(v, w, x, y):
    return w

# Chaotic autonomous complex system 7 (AC7 in Elegant Chaos)
# v(dot) = -x^3 - xy^2 + x^2 - y^2
# w(dot) = -(y^3 + x^2y + 2xy)
# x(dot) = v
# y(dot) = w

def AC7Fv(v, w, x, y):
    return (1 - x)*x*x - (x + 1)*y*y

def AC7Fw(v, w, x, y):
    return -(y*y + x*x + 2*x)*y

def AC7Plot(canvas, w, h, tl):
    tl.set(0)
    g = Graph(0.94, w/2.48, 1.38, h/2.77)
    p = Palette(256, "std")
    vq, wq, xq, yq, s, t = 0, 0, 0.5, 0.5, 0.05, 14801
    for i in range(t):
        if tl.t == 0:
            vp, wp, xp, yp = vq, wq, xq, yq
            vq, wq, xq, yq = rK4(vp, wp, xp, yp, AC7Fv, AC7Fw, v4Fx, w4Fy, s)
            if not tryLine(canvas, g, p, i, xp, yp, xq, yq, 500):
                break
    upd(canvas)

# Rabbit & two foxes
# rabbit co-ords (x1, y1), velocity (u1, v1)
# fox 1 co-ords (x2, y2), velocity (u2, v2)
# fox 2 co-ords (x3, y3), velocity (u3, v3)

def rSq(x1, y1, x2, y2):
    dx = x1 - x2
    dy = y1 - y2
    return dx*dx + dy*dy

def RTF(x1, y1, x2, y2, x3, y3, u1, v1, u2, v2, u3, v3, s):
    r12s = rSq(x1, y1, x2, y2)
    r13s = rSq(x1, y1, x3, y3)
    rx12 = (x1 - x2)/r12s
    rx13 = (x1 - x3)/r13s
    ry12 = (y1 - y2)/r12s
    ry13 = (y1 - y3)/r13s
    u1n = rx12 + rx13 - 3*u1
    v1n = ry12 + ry13 - 3*v1
    u2n = 0.5*(rx12 - u2)
    v2n = 0.5*(ry12 - v2)
    u3n = 0.5*(rx13 - u3)
    v3n = 0.5*(ry13 - v3)
    return u1n*s, v1n*s, u2n*s, v2n*s, u3n*s, v3n*s

def rKRTF(x1, y1, x2, y2, x3, y3, u1, v1, u2, v2, u3, v3, s):
    x11 = u1*s
    y11 = v1*s
    x21 = u2*s
    y21 = v2*s
    x31 = u3*s
    y31 = v3*s
    u11, v11, u21, v21, u31, v31 = \
         RTF(x1, y1, x2, y2, x3, y3, u1, v1, u2, v2, u3, v3, s)
    x12 = (u1 + u11/2)*s
    y12 = (v1 + v11/2)*s
    x22 = (u2 + u21/2)*s
    y22 = (v2 + v21/2)*s
    x32 = (u3 + u31/2)*s
    y32 = (v3 + v31/2)*s
    u12, v12, u22, v22, u32, v32 = \
         RTF(x1 + x11/2, y1 + y11/2, x2 + x21/2, \
             y2 + y21/2, x3 + x31/2, y3 + y31/2, \
             u1 + u11/2, v1 + v11/2, u2 + u21/2, \
             v2 + v21/2, u3 + u31/2, v3 + v31/2, s)
    x13 = (u1 + u12/2)*s
    y13 = (v1 + v12/2)*s
    x23 = (u2 + u22/2)*s
    y23 = (v2 + v22/2)*s
    x33 = (u3 + u32/2)*s
    y33 = (v3 + v32/2)*s
    u13, v13, u23, v23, u33, v33 = \
         RTF(x1 + x12/2, y1 + y12/2, x2 + x22/2, \
             y2 + y22/2, x3 + x32/2, y3 + y32/2, \
             u1 + u12/2, v1 + v12/2, u2 + u22/2, \
             v2 + v22/2, u3 + u32/2, v3 + v32/2, s)
    x14 = (u1 + u13)*s
    y14 = (v1 + v13)*s
    x24 = (u2 + u23)*s
    y24 = (v2 + v23)*s
    x34 = (u3 + u33)*s
    y34 = (v3 + v33)*s
    u14, v14, u24, v24, u34, v34 = \
         RTF(x1 + x13, y1 + y13, x2 + x23, \
             y2 + y23, x3 + x33, y3 + y33, \
             u1 + u13, v1 + v13, u2 + u23, \
             v2 + v23, u3 + u33, v3 + v33, s)
    x1 = x1 + x11/6 + x12/3 + x13/3 + x14/6
    y1 = y1 + y11/6 + y12/3 + y13/3 + y14/6
    x2 = x2 + x21/6 + x22/3 + x23/3 + x24/6
    y2 = y2 + y21/6 + y22/3 + y23/3 + y24/6
    x3 = x3 + x31/6 + x32/3 + x33/3 + x34/6
    y3 = y3 + y31/6 + y32/3 + y33/3 + y34/6
    u1 = u1 + u11/6 + u12/3 + u13/3 + u14/6
    v1 = v1 + v11/6 + v12/3 + v13/3 + v14/6
    u2 = u2 + u21/6 + u22/3 + u23/3 + u24/6
    v2 = v2 + v21/6 + v22/3 + v23/3 + v24/6
    u3 = u3 + u31/6 + u32/3 + u33/3 + u34/6
    v3 = v3 + v31/6 + v32/3 + v33/3 + v34/6
    return x1, y1, x2, y2, x3, y3, u1, v1, u2, v2, u3, v3 

def RTFPlot(canvas, w, h, tl):
    tl.set(1)
    g = Graph(4.23, w/9.07, 8.28, h/12.39)
    p = Palette(256, "std")
    x1q, y1q, x2q, y2q, x3q, y3q, u1q, v1q, u2q, v2q, u3q, v3q = \
        0.5, 1, 1, 0.1, 0, 2, 0, 0, -0.4, 0.4, 0.4, 0
    s, t = 0.05, 30206
    for i in range(t):
        if tl.t == 1:
            x1p, y1p, x2p, y2p, x3p, y3p, u1p, v1p, u2p, v2p, u3p, v3p = \
                x1q, y1q, x2q, y2q, x3q, y3q, u1q, v1q, u2q, v2q, u3q, v3q
            x1q, y1q, x2q, y2q, x3q, y3q, u1q, v1q, u2q, v2q, u3q, v3q = \
                rKRTF(x1p, y1p, x2p, y2p, x3p, y3p, u1p, v1p, u2p, v2p, u3p, v3p, s)
            if not tryLine(canvas, g, p, i, x1p, y1p, x1q, y1q, 500):
                break
    upd(canvas)

class MenuFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent        
        self.initUI()
        self.tl = TaskLock()
    def initUI(self):
        self.WIDTH = 800
        self.HEIGHT = 800
        self.canvas = Canvas(self.parent, width=self.WIDTH, height=self.HEIGHT)
        self.pack(side=BOTTOM)
        self.canvas.pack(side=TOP, fill=BOTH, expand=1)
        self.parent.title("Elegant Chaos")
        menubar = Menu(self.parent)
        self.parent.config(menu=menubar)
        self.parent.protocol('WM_DELETE_WINDOW', self.onExit)
        fileMenu = Menu(menubar)
        fileMenu.add_command(label="Exit", command=self.onExit)
        menubar.add_cascade(label="File", menu=fileMenu)
        ch6Menu = Menu(menubar)
        ch6Menu.add_command(label="Autonomous Complex 7", command=self.onAC7)
        ch6Menu.add_command(label="Rabbit & Two Foxes", command=self.onRTF)
        menubar.add_cascade(label="Chapter 6", menu=ch6Menu)
    def onAC7(self):
        self.canvas.delete("all")
        AC7Plot(self.canvas, self.WIDTH, self.HEIGHT, self.tl)
    def onRTF(self):
        self.canvas.delete("all")
        RTFPlot(self.canvas, self.WIDTH, self.HEIGHT, self.tl)
    def onExit(self):
        self.canvas.delete("all")
        self.parent.destroy()
        
def main():
    root = Tk()
    frame = MenuFrame(root)
    root.mainloop()

if __name__ == '__main__':
    main()
