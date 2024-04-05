# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 12:29:43 2024

@author: spec
"""

import matplotlib.pyplot as plt

import numpy as np

R = 25

H=4*R


p0 = [-R,0]

p1 = [0,R]

p2 = [-R,H-R]
p3 = [0,H]

p4 = [R,H-R]
p5 = [0,R]
p6 = [R,0]


x = np.array([p[0]for p in [p0,p1,p2,p3,p4,p5,p6]])
y = np.array([p[1] for p in [p0,p1,p2,p3,p4,p5,p6]])



theta1 = np.arcsin(2*R/H)


y[2] = H - R - R*np.sin(theta1)
x[2] = -R*np.cos(theta1)


x[1] = -R + R*np.cos(theta1)
y[1] = R + R*np.sin(theta1)

y[4]=y[2]
y[5]=y[1]

x[4] = -x[2]
x[5] = -x[1]







svgtext = """
<?xml version="1.0" ?>
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" version="1.1">
  <path d="PATH" stroke="black" fill="none" stroke_width="2"/>
</svg>"""


path = "M "+str(x[0])+" "+str(y[0])
path += " A "+str(R)+" "+str(R)+" 0 0 1 "+str(x[1])+" "+str(y[1])
path += " L "+str(x[2])+" "+str(y[2])
path += " A "+str(R)+" "+str(R)+" 0 0 0 "+str(x[3])+" "+str(y[3])
path += " A "+str(R)+" "+str(R)+" 0 0 0 "+str(x[4])+" "+str(y[4])
path += " L "+str(x[5])+" "+str(y[5])
path += " A "+str(R)+" "+str(R)+" 0 0 1 "+str(x[6])+" "+str(y[6])


svgtext = svgtext.replace("PATH",path)


f=open('insulationPattern.svg','w')
f.write(svgtext)
f.close()


