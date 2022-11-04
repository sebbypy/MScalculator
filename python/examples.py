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
    example1()
    example2()



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

    shape = 'C-shape'
    
    
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



    



if __name__ == '__main__':
    main()