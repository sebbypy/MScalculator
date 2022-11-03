#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 10 13:22:17 2021

@author: seb
"""

import matplotlib.pyplot as plt
import numpy as np
import MSCalculator_noplot as MS

#import MSCalculator_noplot_nonuniform as MSNU
import MSCalculator_noplot_nonuniform_refactor as MSNU
import MSCalculator_noplot_nonuniform_refactorClass as MSNUnew



def main():

    plt.close('all')
    
    kMetal = 50
    eMetal = 0
    entreAxe = 0.5
    pMetal = 0.022
    wMetal = 0.06
    hMetal = 0.05
    
    Ti=20
    Te=0
    hi=1e5   
    he=1e5

    shape = 'C-shape'
    
    metalProps = {'kMetal':kMetal,'eMetal':eMetal,'entreAxe':entreAxe,'shape':shape,'pMetal':pMetal,'hMetal':hMetal,'wMetal':wMetal}   
    boundaryConditions={'Ti':Ti,'Te':Te,'hi':hi,'he':he}
    
    eIsol = [0.01,0.012,0.07,0.05]
    kIsol=[0.2,0.13,np.nan,1.5]
    
    
    X,Y,T,Rdict = MSNU.MsSolver(eIsol = eIsol,
                               kIsol = kIsol.copy() , 
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
                               Te=Te).solve()
    
    
  
    
    
    X,Y,T,Rdict = MSNUnew.MsSolver(eIsol = eIsol,
                               kIsol = kIsol.copy() , 
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
                               Te=Te).solve()

    
    
    #annotatedPlot(Rdict,metalProps,boundaryConditions,T,eIsol,kIsol,X,Y,grid=False,annotate=True,contour=True)
    


def plotMetalProfile(metalData):

    color='grey'
    if (metalData['shape'] in  ['C-shape','Wood-shape'] ):
        ystart = metalData['entreAxe']/2 - metalData['hMetal']/2
        x1 = metalData['pMetal']
        y1 = ystart
        x2 = x1
        y2 = y1+metalData['hMetal']
        x3 = x1+metalData['wMetal']
        y3=y2
        y4=y1
        x4=x3

    if (metalData['shape'] == 'U-shape'):

        ystart = metalData['entreAxe']/2  + metalData['wMetal']/2
        x1 = metalData['pMetal'] + metalData['hMetal']
        y1 = ystart
        x2 = x1 - metalData['hMetal']
        y2 = y1
        x3 = x2
        y3 = y2 - metalData['wMetal']
        x4=x1
        y4=y3

    x=[x1,x2,x3,x4]
    y=[y1,y2,y3,y4]

        
    if (metalData['shape']=='Wood-shape'):

        x=[x1,x2,x3,x4,x1]
        y=[y1,y2,y3,y4,y1]
        color='brown'
                
    
    plt.plot(y,x,ls='-',color=color,lw=3.0)

    return  x,y


def annotatedPlot(RvaluesDict,metalProps,boundaryConditions,T,eIsol,kIsol,Xuns,Yuns,grid=False,annotate=True,contour=True):

    plt.figure(figsize=(18,6))
    
   
    Rsi = 1/boundaryConditions['hi']
    Rse = 1/boundaryConditions['he']
    
    eCum=0
    for e in eIsol:
        eCum += e
        plt.axhline(eCum,color='k',lw=2.0)

    plotMetalProfile(metalProps)
        
    plt.axis('equal')
   
    if (annotate):        
        plt.annotate('Re = '+str(np.round(Rse,2)),(metalProps['entreAxe']-0.01,eCum+0.01),xycoords='data',horizontalalignment='right')
        plt.annotate('Ri = '+str(np.round(Rsi,2)),(metalProps['entreAxe']-0.01,-0.01),xycoords='data',verticalalignment='top',horizontalalignment='right')


        annotation = 'Layer unpertubed R value: '+str(np.round(RvaluesDict['R1'],2))+' m²K/W\n'
        annotation+= 'Layer calculated R value: '+str(np.round(RvaluesDict['R4'],2))+' m²K/W\n'
        annotation+= 'Layer calculated R value (with RSI + RSE): '+str(np.round(RvaluesDict['R3'],2))+' m²K/W'
    
        plt.annotate(annotation,(0.01,0.8),xycoords='axes fraction',horizontalalignment='left')
        
        hypotheses = ''
        hypotheses +='k$_{metal}$ = '+str(metalProps['kMetal'])+' W/mK\n'
        hypotheses +='Profile thickness = '+str(metalProps['eMetal']*1000)+' mm\n'
        
        plt.annotate(hypotheses,(0.01,-0.01),xycoords='data',horizontalalignment='left',verticalalignment='top')

        eCum=0
        for e,k in zip(eIsol,kIsol):
            
            eCum += e
            
            plt.annotate('e = '+str(e*100)+' cm, k = '+str(k),(0.01,eCum-2e-3),xycoords='data',horizontalalignment='left',verticalalignment='top')
            

    if(grid):
        plt.plot(Yuns,Xuns,'ko',markersize=1)


    if (contour):
        #c=plt.tricontourf(Yuns, Xuns, T,11,cmap='plasma')
        c=plt.tricontourf(Yuns, Xuns, T,11,cmap='coolwarm')
        
        plt.colorbar(ticks=np.linspace(boundaryConditions['Te'],boundaryConditions['Ti'],11,endpoint=True))
   
    #show in cm instead of m    
    xti,xlb = plt.xticks()
    plt.xticks(xti,[str(int(round(100*l))) for l in xti])

    
    yti,ylb = plt.yticks()
    plt.yticks(np.array(yti*100).astype(int)/100,[str(int(round(100*l))) for l in yti])
   
    
    plt.axis('equal')

    plt.savefig('mesh_example.svg')
    



if __name__ == '__main__':
    main()