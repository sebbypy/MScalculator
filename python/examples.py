#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 10 13:22:17 2021

@author: seb
"""

import matplotlib.pyplot as plt
import numpy as np

import MSCalculator
import MSPlotter


def main():

    plt.close('all')
    """example1()
    example2()
    example3()"""
    #example4()
    #example4b()
    example5()
    example6()

def example1():
    
    kMetal = 50
    eMetal = 6e-4
    entreAxe = 0.5
    pMetal = 0.022
    wMetal = 0.05
    hMetal = 0.05
    
    Ti=20
    Te=0
    hi=1e5   
    he=1e5

    shape = 'C-shape'
    
    layersThickness = [0.01,0.012,  0.05, 0.3]
    layersConductivity = [0.2,  0.13, 0.035,  1.5]
    
    
    solver = MSCalculator.MsSolver(layersThickness = layersThickness,
                               layersConductivity = layersConductivity.copy() , 
                               pMetal=pMetal , 
                               wMetal = wMetal, 
                               hMetal = hMetal, 
                               entreAxe = entreAxe,
                               kMetal = kMetal, 
                               eMetal = eMetal, 
                               hi=hi, 
                               he=he, 
                               MStype=shape,
                               Ti=Ti,
                               Te=Te)
    
    solver.solve()

    MSPlotter.annotatedPlot(solver,grid=False,annotate=True,contour=True,saveFig=True,figureName='example1.pdf')

def example2():
    
    kMetal = 50
    eMetal = 6e-4
    entreAxe = 0.5
    pMetal = 0.022
    wMetal = 0.05
    hMetal = 0.05
    
    Ti=20
    Te=0
    hi=10   
    he=25

    shape = 'U-shape'
    
    
    layersThickness = [0.01,0.012,  0.05, 0.05]
    layersConductivity = [0.2,  0.13, np.nan,  1.5]
    
    
    solver = MSCalculator.MsSolver(layersThickness = layersThickness,
                               layersConductivity = layersConductivity.copy() , 
                               pMetal=pMetal , 
                               wMetal = wMetal, 
                               hMetal = hMetal, 
                               entreAxe = entreAxe,
                               kMetal = kMetal, 
                               eMetal = eMetal, 
                               hi=hi, 
                               he=he, 
                               MStype=shape,
                               Ti=Ti,
                               Te=Te)
    
    solver.solve()
    MSPlotter.annotatedPlot(solver,grid=False,contour=True,saveFig=True,figureName='example2.pdf')



def example3():
    
    kMetal = 50
    eMetal = 0
    entreAxe = 0.5
    pMetal = 0.022
    wMetal = 0.05
    hMetal = 0.05
    
    Ti=20
    Te=0
    hi=10   
    he=25

    shape = 'Wood-shape'
    
    
    layersThickness = [0.01,0.012,  0.05, 0.05]
    layersConductivity = [0.2,  0.13, 0.2,  1.5]
    
    
    solver = MSCalculator.MsSolver(layersThickness = layersThickness,
                               layersConductivity = layersConductivity.copy() , 
                               pMetal=pMetal , 
                               wMetal = wMetal, 
                               hMetal = hMetal, 
                               entreAxe = entreAxe,
                               kMetal = kMetal, 
                               eMetal = eMetal, 
                               hi=hi, 
                               he=he, 
                               MStype=shape,
                               Ti=Ti,
                               Te=Te)
    
    solver.solve()
    MSPlotter.annotatedPlot(solver,grid=False,contour=True,saveFig=True,figureName='example2.pdf')



def example4():
    
    kMetal = 50
    eMetal = 6e-4
    entreAxe = 0.3
    pMetal = 0.05

    wMetal = 0.1
    hMetal = 0.1
    
    Ti=20
    Te=0
    hi=10   
    he=10

    shape = 'customProfile'
    
    
    layersThickness = [0.2]
    layersConductivity = [0.035]
    
    
    solver = MSCalculator.MsSolver(layersThickness = layersThickness,
                               layersConductivity = layersConductivity.copy() , 
                               pMetal=pMetal , 
                               wMetal = wMetal, 
                               hMetal = hMetal, 
                               entreAxe = entreAxe,
                               kMetal = kMetal, 
                               eMetal = eMetal, 
                               hi=hi, 
                               he=he, 
                               MStype=shape,
                               Ti=Ti,
                               Te=Te,
                               y0Metal=0.1,
                               h2Metal = 0.1)
    
    solver.solve()
    MSPlotter.annotatedPlot(solver,grid=True,contour=True,saveFig=True,figureName='example4.pdf')


def example4b():
    
    #validation of example 4
    
    kMetal = 50
    eMetal = 6e-4
    entreAxe = 0.3
    pMetal = 0.05

    wMetal = 0.1
    hMetal = 0.1
    
    Ti=20
    Te=0
    hi=10   
    he=10
    shape = 'C-shape'
    
    
    layersThickness = [0.2]
    layersConductivity = [0.035]
    
    
    solver = MSCalculator.MsSolver(layersThickness = layersThickness,
                               layersConductivity = layersConductivity.copy() , 
                               pMetal=pMetal , 
                               wMetal = wMetal, 
                               hMetal = hMetal, 
                               entreAxe = entreAxe,
                               kMetal = kMetal, 
                               eMetal = eMetal, 
                               hi=hi, 
                               he=he, 
                               MStype=shape,
                               Ti=Ti,
                               Te=Te,
                               y0Metal=0.1,
                               h2Metal = 0.1)
    
    solver.solve()
    MSPlotter.annotatedPlot(solver,grid=True,contour=True,saveFig=True,figureName='example4b.pdf')


def example5():
    
    kMetal = 230
    eMetal = 1.5e-3
    entreAxe = 0.5
    pMetal = 0.0

    wMetal = 35e-3
    hMetal = 5e-1
    
    Ti=20
    Te=0
    hi=1/0.11   
    he=1/0.06

    shape = 'customProfile'
    
    
    layersThickness = [35e-3,5e-3,6e-3]
    layersConductivity = [0.029,0.029,1.15]
    
    
    solver = MSCalculator.MsSolver(layersThickness = layersThickness,
                               layersConductivity = layersConductivity.copy() , 
                               pMetal=pMetal , 
                               wMetal = wMetal, 
                               hMetal = hMetal, 
                               entreAxe = entreAxe,
                               kMetal = kMetal, 
                               eMetal = eMetal, 
                               hi=hi, 
                               he=he, 
                               MStype=shape,
                               Ti=Ti,
                               Te=Te,
                               y0Metal=0.0,
                               h2Metal = 0.015,
                               patches=[{'xmin':35e-3,
                                         'xmax':40e-3,
                                         'ymin':0.5-0.015,
                                         'ymax':0.5,
                                         'lambda':0.12}
                                        ])
    
    
    solver.solve()
    MSPlotter.annotatedPlot(solver,grid=False,contour=True,saveFig=False,figureName='example5.pdf',annotate=False,drawLayers=False,orient='horizontal',flipHorizontal=True,
                            pointsToPlot=[
                                {'x':0.046,'y':0.5,'label':'A'},
                                {'x':0.046,'y':0,'label':'B'},
                                {'x':0.040,'y':0.5,'label':'C'},
                                {'x':0.040,'y':0.5-0.015,'label':'D'},
                                {'x':0.040,'y':0,'label':'E'},
                                {'x':0.035,'y':0.5,'label':'F'},
                                {'x':0.035,'y':0.5-0.015,'label':'G'},
                                {'x':0.0,'y':0.5,'label':'H'},                             
                                {'x':0.0,'y':0,'label':'I'},
                                ])


    plt.gcf().axes[0].axis('equal')
    plt.gcf().axes[0].set_xlim(left=-0.02,right=0.10)
    plt.savefig('tescase2-left.pdf')

    plt.gcf().axes[0].set_xlim(left=0.40,right=0.502)
    plt.savefig('tescase2-right.pdf')

    #plt.gcf().axes[0].set_ylim(bottom=-0.005,top=0.050)


    #plt.gcf().axes[0].set_ylim(bottom=-0.005,top=0.1)
    
    
    heatFlux = solver.computeWallHeatFlux()
    print("Heat flux",heatFlux)


def example6():
    
    
    kMetal = 50
    eMetal = 0
    
    entreAxe = 0.5

    pMetal = 0.05
    wMetal = 0.1
    hMetal = 0.1
    
    Ti=0
    Te=20
    hi=1e5   
    he=1e5
    shape = 'C-shape'
    
    
    layersThickness = [entreAxe*2]
    layersConductivity = [1]
    
    
    solver = MSCalculator.MsSolver(layersThickness = layersThickness,
                                   layersConductivity = layersConductivity.copy() , 
                                   pMetal=pMetal , 
                                   wMetal = wMetal, 
                                   hMetal = hMetal, 
                                   entreAxe = entreAxe,
                                   kMetal = kMetal, 
                                   eMetal = eMetal, 
                                   hi=hi, 
                                   he=he, 
                                   MStype=shape,
                                   Ti=Ti,
                                   Te=Te,
                                   topBC=0)
        
    solver.solve()

    
    gridstep = float(1/8)
    
    pointsToPlot = []
    
    for i in range(1,8):
        xi = i*gridstep

        for j in range(0,4):
            yi = j*gridstep
            
            pointsToPlot.append({'x':xi,'y':yi,'label':''})




    MSPlotter.annotatedPlot(solver,grid=False,contour=True,saveFig=True,figureName='example6.pdf',orient='horizontal',flipHorizontal=True,pointsToPlot=pointsToPlot,annotate=False,drawLayers=False)


if __name__ == '__main__':
    main()