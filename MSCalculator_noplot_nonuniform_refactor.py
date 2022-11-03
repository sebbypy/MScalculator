# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 09:35:28 2021

@author: spec
"""

#METAL STUD 2d SOLVER

import numpy as np
    
import sys
#Non uniform version to have an automatic mesh with variable step size. 

#Imagined mesh rules:
# max .5 cm on an area of twice the size of the MS profile
# 1 cm elsewhere or even more in the X direct
# handle mm thickness. 




def genMesh(*,eIsol,pMetal,wMetal,hMetal,shape,entreAxe):
    
    sizeMS = 5e-3
    sizeOther = 2e-2
    
    
    if shape=='C-shape':
        metalXspan = wMetal
        metalYspan = hMetal
    if shape=='U-shape':
        metalYspan = wMetal
        metalXspan = hMetal

    pMetal = pMetal
    entreAxe = entreAxe
    
    xticks=[0]
    cum=0
    for e in eIsol:
        #xticks.append(cum+e/2)
        xticks.append(cum+e)
        cum += e

    xticks.append(pMetal)
    xticks.append(pMetal+metalXspan)
    xticks = list(set(xticks))

    xticks.sort()    
    xticks = refineGloballyX(xticks,sizeOther)
    xticks = refineMS(xticks,pMetal,metalXspan,sizeMS)

    
    #yticks management
    yticks = [0,
              entreAxe/2-metalYspan/2,
              entreAxe/2+metalYspan/2,
              entreAxe
              ]
    yticks = refineGloballyX(yticks,sizeOther)
    yticks = refineMS(yticks,(entreAxe-metalYspan)/2,metalYspan,sizeMS)
    
    
    return [xticks,yticks]
    


def genUniformMesh(*,eIsol,pMetal,wMetal,hMetal,shape,entreAxe):

    size = 1e-2
    
    if shape=='C-shape':
        metalXspan = wMetal
        metalYspan = hMetal
    if shape=='U-shape':
        metalYspan = wMetal
        metalXspan = hMetal

    pMetal = pMetal
    entreAxe = entreAxe
    
    xticks=[0]
    cum=0
    for e in eIsol:
        #xticks.append(cum+e/2)
        xticks.append(cum+e)
        cum += e

    xticks.append(pMetal)
    xticks.append(pMetal+metalXspan)

    xticks = list(set(xticks))

    xticks.sort()    
    xticks = refineGloballyX(xticks,size)


    #yticks management
    yticks = [0,
              entreAxe/2-metalYspan/2,
              entreAxe/2+metalYspan/2,
              entreAxe
              ]
    yticks = refineGloballyX(yticks,size)
    
    
    return [xticks,yticks]



def refineGloballyX(inputTicks,maxdx):
   
    pointsToAdd=[]
    

    #print(inputTicks)
    
    xprev=0
    for xpos in inputTicks:
        if (xpos==0):
            continue
        
        pointsToAdd += refineInterval(xprev,xpos,maxdx)
        xprev=xpos
        
    outputTicks = inputTicks + pointsToAdd
    outputTicks.sort()
    
    return outputTicks

def refineMS(inputTicks,pMetal,dxMetal,maxdx):
    
    pointsToAdd=[]
    
    xprev=0
    for xpos in inputTicks:
        if (xpos==0):
            continue
    
        if ( isInMetalStudArea(xprev,pMetal,dxMetal) or isInMetalStudArea(xpos,pMetal,dxMetal)):    
            pointsToAdd += refineInterval(xprev,xpos,maxdx)

        xprev=xpos

    
    outputTicks = inputTicks + pointsToAdd
    outputTicks.sort()
    
    return outputTicks
    
    

def refineInterval(xstart,xend,maxdx):

    tol=1e-4
       
    dx = xend-xstart   
    
    numberOfIntervals = int(np.ceil( (dx-tol)/maxdx ))
    
    if (numberOfIntervals==0):
        numberOfIntervals=1
    
    numberOfPointsToAdd = numberOfIntervals-1
    
    newdx = dx/numberOfIntervals

    newPoints=[]
    
    for newPointI in range(numberOfPointsToAdd):
        newPoints.append(xstart + (newPointI+1)*newdx)

    return newPoints

    

def isInMetalStudArea(x,pMetal,spanMetal):
      
    margin = spanMetal/2
    
    if (  x > pMetal - margin and x <= pMetal + spanMetal +margin ):
        return True
    
    else:
        return False


class MsSolver:
    
    def __init__(self,*,eIsol = [0.2] , kIsol=[0.035], pMetal=0.0, wMetal = 0.05, hMetal = 0.05, entreAxe = 0.6, kMetal = 50, eMetal=6e-4, hi=10, he=10, MStype='U-shape',Ti=20,Te=0,mesh='nonuniform',ResistanceAirLayer=0.18):
        
        self.eIsol=eIsol
        self.kIsol=kIsol
        self.pMetal=pMetal
        self.wMetal=wMetal
        self.entreAxe = entreAxe
        self.kMetal = kMetal
        self.eMetal = eMetal
        self.hMetal = hMetal
        self.hi = hi
        self.he = he
        self.Ti = Ti
        self.Te = Te
        self.mesh = mesh
        self.MStype = MStype
        self.ResitanceAirLayer =  ResistanceAirLayer
        
    
    def solve(self):
        
        
        self.genMesh()
        self.computeCellProperties()
        self.fillMatrices()
        
        self.T = np.linalg.solve(self.A, self.b)
    

        
        metalProps = {'kMetal':self.kMetal,'eMetal':self.eMetal,'entreAxe':self.entreAxe}   
        boundaryConditions={'Ti':self.Ti,'Te':self.Te,'hi':self.hi,'he':self.he}

        heatFlux = self.computeWallHeatFlux()        
        Xuns,Yuns = self.getFlattenedXandY()
        
        RvaluesDict = computeUandRValues(heatFlux,metalProps,boundaryConditions,self.npy,self.T,self.npoints,self.eIsol,self.kIsol,Xuns,Yuns)
    
        return [Xuns,Yuns,self.T,RvaluesDict]

        
        
    
    def genMesh(self):
          
          #def genMesh(*,eIsol,pMetal,wMetal,hMetal,shape,entreAxe):
    
        sizeMS = 5e-3
        sizeOther = 2e-2
        
        
        if self.MStype=='C-shape':
            metalXspan = self.wMetal
            metalYspan = self.hMetal
        if self.MStype=='U-shape':
            metalYspan = self.wMetal
            metalXspan = self.hMetal
        
        #pMetal = pMetal
        #entreAxe = entreAxe
        
        xticks=[0]
        cum=0
        for e in self.eIsol:
            #xticks.append(cum+e/2)
            xticks.append(cum+e)
            cum += e
        
        xticks.append(self.pMetal)
        xticks.append(self.pMetal+metalXspan)
        xticks = list(set(xticks))
        
        xticks.sort()    
        xticks = refineGloballyX(xticks,sizeOther)
        xticks = refineMS(xticks,self.pMetal,metalXspan,sizeMS)
        
        
        #yticks management
        yticks = [0,
                  self.entreAxe/2-metalYspan/2,
                  self.entreAxe/2+metalYspan/2,
                  self.entreAxe
                  ]
        yticks = refineGloballyX(yticks,sizeOther)
        yticks = refineMS(yticks,(self.entreAxe-metalYspan)/2,metalYspan,sizeMS)
        
        self.xticks = np.array(xticks)
        self.yticks = np.array(yticks)        
        
        self.npx = len(xticks)
        self.npy = len(yticks)
        self.npoints = self.npx*self.npy
        

    def computeCellProperties(self):
        
        if np.nan in self.kIsol:       
            self.airLayerPosition = self.kIsol.index(np.nan)
            self.kIsol[self.airLayerPosition] = 1000
        else:
            self.airLayerPosition = None

        
        kI = computeNodesLeftAndRightConductivity(self.eIsol,self.kIsol,self.xticks)
        nodeTypes = computeNodeType(self.eIsol,self.kIsol,self.airLayerPosition,self.xticks)
        
        
        self.kI = kI
        self.nodeTypes = nodeTypes
    
    
    def getLeftAndRightK(self,i):
        
        return self.kI[i,0],self.kI[i,1]

    def fillMatrices(self):
        
        
        self.A = np.zeros((self.npoints,self.npoints))
        self.b = np.zeros(self.npoints)
        self.T=np.zeros(self.npoints)

        MS_ids,nMSNodes,xMetal,yMetal = mapMetalNodes(self.xticks,self.yticks,self.MStype,self.wMetal,self.hMetal,self.pMetal) # table that contains -1 if nothing special or a null or positive id  if MS


        hair= 1/(self.ResitanceAirLayer/2)


        for i in range(self.npx):
            
            for j in range(self.npy):
    
                n = self.getNodeNumber(i,j)
                neighbours = self.getNodeNeighbours(i,j) #its a dict

                nValues = neighbours.copy()
                nValues['n'] = n
                
                kLeft,kRight = self.getLeftAndRightK(i)
    
                
                DxAndDy = getDxDy(self.xticks,self.yticks,i,j)            
                cellAreas = getCellAreas(self.xticks,self.yticks,i,j)
    
                
                #case 1 : normal cell
                if (i>0 and j>0 and i<self.npx-1 and j<self.npy-1):
    
                    if self.nodeTypes[i] == "AirLayerLeftBoundary":
                       
                        self.addConductionFlux(nValues,DxAndDy,cellAreas,['downLeft','leftDown','leftUp','upLeft'],
                                           kLeft,kRight)
                        
                        self.addConvectiveFlux(nValues,DxAndDy,cellAreas,['rightUp','rightDown'],
                                           kLeft,kRight,hair)
                        
    
                    elif self.nodeTypes[i] == "AirLayerFirstNodeAfterLeftBoundary":
    
                        self.addConductionFlux(nValues,DxAndDy,cellAreas,['downRight','rightDown','rightUp','upRight'],
                                           kLeft,kRight)
                        
                        self.addConvectiveFlux(nValues,DxAndDy,cellAreas,['leftUp','leftDown'],
                                           kLeft,kRight,hair)
    
                        
                    elif self.nodeTypes[i] == "AirLayerLastNodeBeforeRightBoundary":
    
                        self.addConductionFlux(nValues,DxAndDy,cellAreas,['downLeft','leftDown','leftUp','upLeft'],
                                           kLeft,kRight)
                        
                        self.addConvectiveFlux(nValues,DxAndDy,cellAreas,['rightUp','rightDown'],
                                           kLeft,kRight,hair)
                        
    
                    elif self.nodeTypes[i] == "AirLayerRightBoundary":
    
                        self.addConductionFlux(nValues,DxAndDy,cellAreas,['downRight','rightDown','rightUp','upRight'],
                                           kLeft,kRight)
                        
                        self.addConvectiveFlux(nValues,DxAndDy,cellAreas,['leftUp','leftDown'],
                                           kLeft,kRight,hair)
    
    
                    else: #normal node
                     
                        self.addConductionFlux(nValues,DxAndDy,cellAreas,
                                          ['rightUp','rightDown',
                                           'downRight','downLeft',
                                           'leftDown','leftUp',
                                           'upLeft','upRight'],
                                           kLeft,kRight)
                        
                
                #case 2: normal left BC
                if (i==0 and (j !=0 and j != self.npy-1)):
    
                    self.addConductionFlux(nValues,DxAndDy,cellAreas,
                                      ['rightUp','rightDown','upRight','downRight'],kLeft,kRight)
    
                    self.addConvectiveBC(nValues,DxAndDy,cellAreas,
                                      ['leftUp','leftDown'],kLeft,kRight,self.hi,self.Ti)
    
                #botm left 
                if (i==0 and j==0):
                    
                    self.addConductionFlux(nValues,DxAndDy,cellAreas,['upRight','rightUp'],kLeft,kRight)              
                    self.addConvectiveBC(nValues,DxAndDy,cellAreas,['leftUp'],kLeft,kRight,self.hi,self.Ti)
    
    
                #top left                
                if (i==0 and j==self.npy-1):
    
                    self.addConductionFlux(nValues,DxAndDy,cellAreas,['downRight','rightDown'],kLeft,kRight)              
                    self.addConvectiveBC(nValues,DxAndDy,cellAreas,['leftDown'],kLeft,kRight,self.hi,self.Ti)
    
    
                #case 2: normal right
                if (i== self.npx-1 and (j !=0 and j != self.npy-1)):
                
                    self.addConductionFlux(nValues,DxAndDy,cellAreas,
                                      ['leftUp','leftDown','upLeft','downLeft'],kLeft,kRight)
    
                    self.addConvectiveBC(nValues,DxAndDy,cellAreas,['rightUp','rightDown'],kLeft,kRight,self.he,self.Te)
    
                
                #case 4: normal bot: symmetric
                if (j== 0 and (i !=0 and i != self.npx-1)):
    
                    if self.nodeTypes[i] == "AirLayerLeftBoundary":
                        
                        self.addConductionFlux(nValues,DxAndDy,cellAreas,['upLeft','leftUp'],kLeft,kRight)
                        self.addConvectiveFlux(nValues,DxAndDy,cellAreas,['rightUp'],kLeft,kRight,hair)
    
                    elif self.nodeTypes[i] == "AirLayerFirstNodeAfterLeftBoundary":
                        
                        self.addConductionFlux(nValues,DxAndDy,cellAreas,['upLeft','upRight','rightUp'],kLeft,kRight)
                        self.addConvectiveFlux(nValues,DxAndDy,cellAreas,['leftUp'],kLeft,kRight,hair)
    
                    elif self.nodeTypes[i] == "AirLayerLastNodeBeforeRightBoundary":
                        
                        self.addConductionFlux(nValues,DxAndDy,cellAreas,['upLeft','upRight','leftUp'],kLeft,kRight)                
                        self.addConvectiveFlux(nValues,DxAndDy,cellAreas,['rightUp'],kLeft,kRight,hair)
    
                    elif self.nodeTypes[i] == "AirLayerRightBoundary":
    
                        self.addConductionFlux(nValues,DxAndDy,cellAreas,['upRight','rightUp'],kLeft,kRight)                    
                        self.addConvectiveFlux(nValues,DxAndDy,cellAreas,['leftUp'],kLeft,kRight,hair)
                        
    
                    else:               
                        self.addConductionFlux(nValues,DxAndDy,cellAreas,['rightUp','upRight','upLeft','leftUp'],kLeft,kRight)
                    
    
                    
                #case 5: normal top: symmetric
                if (j== self.npy-1 and (i !=0 and i != self.npx-1)):
    
                    if self.nodeTypes[i] == "AirLayerLeftBoundary":
                        
                        self.addConductionFlux(nValues,DxAndDy,cellAreas,
                                           ['downLeft','leftDown'],
                                           kLeft,kRight)
                        
                        self.addConvectiveFlux(nValues,DxAndDy,cellAreas,
                                           ['rightDown'],
                                           kLeft,kRight,hair)
    
                    elif self.nodeTypes[i] == "AirLayerFirstNodeAfterLeftBoundary":
                        
                        self.addConductionFlux(nValues,DxAndDy,cellAreas,
                                           ['downLeft','downRight','rightDown'],
                                           kLeft,kRight)
                        
                        self.addConvectiveFlux(nValues,DxAndDy,cellAreas,
                                           ['leftDown'],
                                           kLeft,kRight,hair)
    
                    elif self.nodeTypes[i] == "AirLayerLastNodeBeforeRightBoundary":
                        
                        self.addConductionFlux(nValues,DxAndDy,cellAreas,
                                           ['downLeft','downRight','leftDown'],
                                           kLeft,kRight)
                        
                        self.addConvectiveFlux(nValues,DxAndDy,cellAreas,
                                           ['rightDown'],
                                           kLeft,kRight,hair)
    
                    elif self.nodeTypes[i] == "AirLayerRightBoundary":
    
                        self.addConductionFlux(nValues,DxAndDy,cellAreas,
                                           ['downRight','rightDown'],
                                           kLeft,kRight)
                        
                        self.addConvectiveFlux(nValues,DxAndDy,cellAreas,
                                           ['leftDown'],
                                           kLeft,kRight,hair)
                        
                    else:
                        self.addConductionFlux(nValues,DxAndDy,cellAreas,
                                          ['rightDown','downRight','downLeft','leftDown'],
                                           kLeft,kRight)              
    
    
                #bot right                
                if (i==self.npx-1 and j==0):
    
                    self.addConductionFlux(nValues,DxAndDy,cellAreas,['upLeft','leftUp'],kLeft,kRight)              
                    self.addConvectiveBC(nValues,DxAndDy,cellAreas,['rightUp'],kLeft,kRight,self.he,self.Te)
    
                #top right
                if (i==self.npx-1 and j==self.npy-1):
                    
                    self.addConductionFlux(nValues,DxAndDy,cellAreas,['downLeft','leftDown'],kLeft,kRight)              
                    self.addConvectiveBC(nValues,DxAndDy,cellAreas,['rightDown'],kLeft,kRight,self.he,self.Te)
    
                    
    
                if isMetalNode(i,j,MS_ids):    
    
                    MSID,nMS_prev,nMS_next = getMetalNodesIDS(i,j,MS_ids,self.npy)
    
                    
                    currentPoint  = [ xMetal[MSID]  , yMetal[MSID] ]
                    if (MSID>0):
                        previousPoint = [ xMetal[MSID-1], yMetal[MSID-1] ]
    
                    if(MSID<nMSNodes-1):
                        nextPoint     = [ xMetal[MSID+1], yMetal[MSID+1] ]
    
                    if MSID == 0:
                        
                        distanceToNext = dist(currentPoint,nextPoint)
    
                        self.A[n,n]        += -1*self.kMetal*self.eMetal/distanceToNext
                        self.A[n,nMS_next] += self.kMetal*self.eMetal/distanceToNext
                        
                    elif MSID == nMSNodes -1:
                        
                        distanceToPrevious = dist(currentPoint,previousPoint)   
                        self.A[n,n] += -1*self.kMetal*self.eMetal/distanceToPrevious
                        self.A[n,nMS_prev] += self.kMetal*self.eMetal/distanceToPrevious
                    
                    else:
                        distanceToNext = dist(currentPoint,nextPoint)
                        distanceToPrevious = dist(currentPoint,previousPoint)   
        
                        self.A[n,nMS_prev] += self.kMetal*self.eMetal/distanceToPrevious
                        self.A[n,nMS_next] += self.kMetal*self.eMetal/distanceToNext
                        self.A[n,n] += -self.kMetal*self.eMetal*(1/distanceToPrevious + 1/distanceToNext)
            


    def getNodeNeighbours(self,i,j):
        
        nLeft = nRight = nUp = nDown = np.nan
        
        if (i>0):
            nLeft  = getGlobalNodeNumber(i-1,j,self.npy)
        if (i<self.npx-1):
            nRight = getGlobalNodeNumber(i+1,j,self.npy)
                
        if (j>0):
            nDown = getGlobalNodeNumber(i,j-1,self.npy)
        if (j<self.npy-1):
            nUp   = getGlobalNodeNumber(i,j+1,self.npy)
    
        return {'nLeft':nLeft,'nRight':nRight,'nDown':nDown,'nUp':nUp}

    
    def getNodeNumber(self,i,j):
    
        return i*self.npy + j

    
    
    def addConductionFlux(self,nValues,DxAndDy, cellAreas,fluxes,kLeft,kRight):

        dxLeft,dxRight,dyUp,dyDown = DxAndDy                   
        AUpDownLeft,AUpDownRight,ALeftRightDown,ALeftRightUp = cellAreas

        n = nValues['n']
        nLeft  = nValues['nLeft']
        nRight = nValues['nRight']
        nUp = nValues['nUp']
        nDown = nValues['nDown']


        for flux in fluxes:
            
            if flux=='upRight':
                upRight = kRight*AUpDownRight/dyUp

                self.A[n,n] += -upRight
                self.A[n,nUp] += upRight
                
            elif flux=='upLeft':            
                upLeft  = kLeft*AUpDownLeft/dyUp
                self.A[n,n] += -upLeft
                self.A[n,nUp] += upLeft

            if flux=='downRight':
                downRight = kRight*AUpDownRight/dyDown

                self.A[n,n] += -downRight
                self.A[n,nDown] += downRight
                
            if flux=='downLeft':            
                downLeft  = kLeft*AUpDownLeft/dyDown
                self.A[n,n] += -downLeft
                self.A[n,nDown] += downLeft

            if flux=='rightUp':
                rightUp   = kRight*ALeftRightUp/dxRight

                self.A[n,n] += -rightUp
                self.A[n,nRight] += rightUp

            if flux=='rightDown':
                rightDown   = kRight*ALeftRightDown/dxRight

                self.A[n,n] += -rightDown
                self.A[n,nRight] += rightDown


            if flux=='leftUp':
                leftUp   = kLeft*ALeftRightUp/dxLeft

                self.A[n,n] += -leftUp
                self.A[n,nLeft] += leftUp

            if flux=='leftDown':
                leftDown   = kLeft*ALeftRightDown/dxLeft

                self.A[n,n] += -leftDown
                self.A[n,nLeft] += leftDown


    def addConvectiveFlux(self,nValues,DxAndDy, cellAreas,fluxes,kLeft,kRight,hValue):
    
            dxLeft,dxRight,dyUp,dyDown = DxAndDy                   
            AUpDownLeft,AUpDownRight,ALeftRightDown,ALeftRightUp = cellAreas
    
            n = nValues['n']
            nLeft  = nValues['nLeft']
            nRight = nValues['nRight']

    
            for flux in fluxes:
    
                if flux=='rightUp':
                    rightUp   = hValue*ALeftRightUp
                    self.A[n,n] += -rightUp
                    self.A[n,nRight] += rightUp
    
                if flux=='rightDown':
                    rightDown = hValue*ALeftRightDown
                    self.A[n,n] += -rightDown
                    self.A[n,nRight] += rightDown
    
    
                if flux=='leftUp':
                    leftUp   = hValue*ALeftRightUp
                    self.A[n,n] += -leftUp
                    self.A[n,nLeft] += leftUp
    
                if flux=='leftDown':
                    leftDown   = hValue*ALeftRightDown
                    self.A[n,n] += -leftDown
                    self.A[n,nLeft] += leftDown
            

    def addConvectiveBC(self,nValues,DxAndDy, cellAreas,fluxes,kLeft,kRight,hc,Tb):

        dxLeft,dxRight,dyUp,dyDown = DxAndDy                   
        AUpDownLeft,AUpDownRight,ALeftRightDown,ALeftRightUp = cellAreas

        n = nValues['n']

        for flux in fluxes:
            
            
            if (flux=='leftUp'):
                
                self.A[n,n] += -hc*ALeftRightUp #convective
                self.b[n]   += -hc*Tb*ALeftRightUp

            if (flux=='leftDown'):

                self.A[n,n] += -hc*ALeftRightDown #convective
                self.b[n]   += -hc*Tb*ALeftRightDown
    
            if (flux=='rightUp'):
                
                self.A[n,n] += -hc*ALeftRightUp #convective
                self.b[n]   += -hc*Tb*ALeftRightUp

            if (flux=='rightDown'):

                self.A[n,n] += -hc*ALeftRightDown #convective
                self.b[n]   += -hc*Tb*ALeftRightDown


    def computeWallHeatFlux(self):
        
        heatFlux = 0
        totalLenght= 0 
        for interval in range(1,self.npy):
            intervalLength = self.yticks[interval]-self.yticks[interval-1]
            intervalMeanT   = (self.T[interval]+self.T[interval-1])/2       #the N first nodes are the left bc
            intervalFlux   = self.hi*(self.Ti-intervalMeanT)*intervalLength
    
            totalLenght +=intervalLength
            heatFlux += intervalFlux
    
    
        return heatFlux


    def getFlattenedXandY(self):
        
        Xuns = np.zeros(self.npoints)
        Yuns = np.zeros(self.npoints)
        
        for i in range(self.npx):
            for j in range(self.npy):
                
                n = self.getNodeNumber(i,j)
                
                Xuns[n] = self.xticks[i]
                Yuns[n] = self.yticks[j]
        

        return Xuns,Yuns        

    

def multiLayer_hConv_MS(*,eIsol = [0.2] , kIsol=[0.035], pMetal=0.0, wMetal = 0.05, hMetal = 0.05, entreAxe = 0.6, kMetal = 50, eMetal=6e-4, hi=10, he=10, MStype='U-shape',Ti=20,Te=0,mesh='nonuniform'):

    if mesh == 'nonuniform':    
        xticks,yticks = genMesh(eIsol=eIsol,pMetal=pMetal,wMetal=wMetal,hMetal=hMetal,entreAxe=entreAxe,shape=MStype)
    else:
        xticks,yticks = genUniformMesh(eIsol=eIsol,pMetal=pMetal,wMetal=wMetal,hMetal=hMetal,entreAxe=entreAxe,shape=MStype)

    #sign that there is an air layer
    if np.nan in kIsol:       
        airLayerPosition = kIsol.index(np.nan)
        kIsol[airLayerPosition] = 1000
    else:
        airLayerPosition = None

    xticks=np.array(xticks)
    yticks=np.array(yticks)
    
    npx = len(xticks)
    npy = len(yticks)
    
    npoints = npx*npy


    kI = computeNodesLeftAndRightConductivity(eIsol,kIsol,xticks)
    nodeTypes = computeNodeType(eIsol,kIsol,airLayerPosition,xticks)
    

    MS_ids,nMSNodes,xMetal,yMetal = mapMetalNodes(xticks,yticks,MStype,wMetal,hMetal,pMetal) # table that contains -1 if nothing special or a null or positive id  if MS


    A = np.zeros((npoints,npoints))
    b = np.zeros(npoints)
    T=np.zeros(npoints)
    
    #Unstructured coordinates
    Xuns=np.zeros(npoints)
    Yuns=np.zeros(npoints)
    
    
    for i in range(npx):
        
        for j in range(npy):

            
            nValues = getNodeAndNeighbours(i,j,npx,npy)
            n = nValues[0]
            
            Xuns[n] = xticks[i]
            Yuns[n] = yticks[j]
         
            kLeft  = kI[i,0]
            kRight = kI[i,1]

            
            DxAndDy = getDxDy(xticks,yticks,i,j)            
            cellAreas = getCellAreas(xticks,yticks,i,j)
            

            
            hair= 1
            #case 1 : normal cell
            if (i>0 and j>0 and i<npx-1 and j<npy-1):

                if nodeTypes[i] == "AirLayerLeftBoundary":
                   
                    addConductionFlux(A,b,nValues,DxAndDy,cellAreas,['downLeft','leftDown','leftUp','upLeft'],
                                       kLeft,kRight)
                    
                    addConvectiveFlux(A,b,nValues,DxAndDy,cellAreas,['rightUp','rightDown'],
                                       kLeft,kRight,hair)
                    

                elif nodeTypes[i] == "AirLayerFirstNodeAfterLeftBoundary":

                    addConductionFlux(A,b,nValues,DxAndDy,cellAreas,['downRight','rightDown','rightUp','upRight'],
                                       kLeft,kRight)
                    
                    addConvectiveFlux(A,b,nValues,DxAndDy,cellAreas,['leftUp','leftDown'],
                                       kLeft,kRight,hair)

                    
                elif nodeTypes[i] == "AirLayerLastNodeBeforeRightBoundary":

                    addConductionFlux(A,b,nValues,DxAndDy,cellAreas,['downLeft','leftDown','leftUp','upLeft'],
                                       kLeft,kRight)
                    
                    addConvectiveFlux(A,b,nValues,DxAndDy,cellAreas,['rightUp','rightDown'],
                                       kLeft,kRight,hair)
                    

                elif nodeTypes[i] == "AirLayerRightBoundary":

                    addConductionFlux(A,b,nValues,DxAndDy,cellAreas,['downRight','rightDown','rightUp','upRight'],
                                       kLeft,kRight)
                    
                    addConvectiveFlux(A,b,nValues,DxAndDy,cellAreas,['leftUp','leftDown'],
                                       kLeft,kRight,hair)


                else: #normal node
                    
                    b[n] = 0

                    addConductionFlux(A,b,nValues,DxAndDy,cellAreas,
                                      ['rightUp','rightDown',
                                       'downRight','downLeft',
                                       'leftDown','leftUp',
                                       'upLeft','upRight'],
                                       kLeft,kRight)
                    
            
            #case 2: normal left BC
            if (i==0 and (j !=0 and j != npy-1)):

                addConductionFlux(A,b,nValues,DxAndDy,cellAreas,
                                  ['rightUp','rightDown','upRight','downRight'],kLeft,kRight)

                addConvectiveBC(A,b,nValues,DxAndDy,cellAreas,
                                  ['leftUp','leftDown'],kLeft,kRight,hi,Ti)

            #botm left 
            if (i==0 and j==0):
                
                addConductionFlux(A,b,nValues,DxAndDy,cellAreas,['upRight','rightUp'],kLeft,kRight)              
                addConvectiveBC(A,b,nValues,DxAndDy,cellAreas,['leftUp'],kLeft,kRight,hi,Ti)


            #top left                
            if (i==0 and j==npy-1):

                addConductionFlux(A,b,nValues,DxAndDy,cellAreas,['downRight','rightDown'],kLeft,kRight)              
                addConvectiveBC(A,b,nValues,DxAndDy,cellAreas,['leftDown'],kLeft,kRight,hi,Ti)


            #case 2: normal right
            if (i== npx-1 and (j !=0 and j != npy-1)):
            
                addConductionFlux(A,b,nValues,DxAndDy,cellAreas,
                                  ['leftUp','leftDown','upLeft','downLeft'],kLeft,kRight)

                addConvectiveBC(A,b,nValues,DxAndDy,cellAreas,['rightUp','rightDown'],kLeft,kRight,he,Te)

            
            #case 4: normal bot: symmetric
            if (j== 0 and (i !=0 and i != npx-1)):

                if nodeTypes[i] == "AirLayerLeftBoundary":
                    
                    addConductionFlux(A,b,nValues,DxAndDy,cellAreas,['upLeft','leftUp'],kLeft,kRight)
                    addConvectiveFlux(A,b,nValues,DxAndDy,cellAreas,['rightUp'],kLeft,kRight,hair)

                elif nodeTypes[i] == "AirLayerFirstNodeAfterLeftBoundary":
                    
                    addConductionFlux(A,b,nValues,DxAndDy,cellAreas,['upLeft','upRight','rightUp'],kLeft,kRight)
                    addConvectiveFlux(A,b,nValues,DxAndDy,cellAreas,['leftUp'],kLeft,kRight,hair)

                elif nodeTypes[i] == "AirLayerLastNodeBeforeRightBoundary":
                    
                    addConductionFlux(A,b,nValues,DxAndDy,cellAreas,['upLeft','upRight','leftUp'],kLeft,kRight)                
                    addConvectiveFlux(A,b,nValues,DxAndDy,cellAreas,['rightUp'],kLeft,kRight,hair)

                elif nodeTypes[i] == "AirLayerRightBoundary":

                    addConductionFlux(A,b,nValues,DxAndDy,cellAreas,['upRight','rightUp'],kLeft,kRight)                    
                    addConvectiveFlux(A,b,nValues,DxAndDy,cellAreas,['leftUp'],kLeft,kRight,hair)
                    

                else:               
                    addConductionFlux(A,b,nValues,DxAndDy,cellAreas,['rightUp','upRight','upLeft','leftUp'],kLeft,kRight)
                

                
            #case 5: normal top: symmetric
            if (j== npy-1 and (i !=0 and i != npx-1)):

                if nodeTypes[i] == "AirLayerLeftBoundary":
                    
                    addConductionFlux(A,b,nValues,DxAndDy,cellAreas,
                                       ['downLeft','leftDown'],
                                       kLeft,kRight)
                    
                    addConvectiveFlux(A,b,nValues,DxAndDy,cellAreas,
                                       ['rightDown'],
                                       kLeft,kRight,hair)

                elif nodeTypes[i] == "AirLayerFirstNodeAfterLeftBoundary":
                    
                    addConductionFlux(A,b,nValues,DxAndDy,cellAreas,
                                       ['downLeft','downRight','rightDown'],
                                       kLeft,kRight)
                    
                    addConvectiveFlux(A,b,nValues,DxAndDy,cellAreas,
                                       ['leftDown'],
                                       kLeft,kRight,hair)

                elif nodeTypes[i] == "AirLayerLastNodeBeforeRightBoundary":
                    
                    addConductionFlux(A,b,nValues,DxAndDy,cellAreas,
                                       ['downLeft','downRight','leftDown'],
                                       kLeft,kRight)
                    
                    addConvectiveFlux(A,b,nValues,DxAndDy,cellAreas,
                                       ['rightDown'],
                                       kLeft,kRight,hair)

                elif nodeTypes[i] == "AirLayerRightBoundary":

                    addConductionFlux(A,b,nValues,DxAndDy,cellAreas,
                                       ['downRight','rightDown'],
                                       kLeft,kRight)
                    
                    addConvectiveFlux(A,b,nValues,DxAndDy,cellAreas,
                                       ['leftDown'],
                                       kLeft,kRight,hair)
                    
                else:
                    addConductionFlux(A,b,nValues,DxAndDy,cellAreas,
                                      ['rightDown','downRight','downLeft','leftDown'],
                                       kLeft,kRight)              


            #bot right                
            if (i==npx-1 and j==0):

                addConductionFlux(A,b,nValues,DxAndDy,cellAreas,['upLeft','leftUp'],kLeft,kRight)              
                addConvectiveBC(A,b,nValues,DxAndDy,cellAreas,['rightUp'],kLeft,kRight,he,Te)

            #top right
            if (i==npx-1 and j==npy-1):
                
                addConductionFlux(A,b,nValues,DxAndDy,cellAreas,['downLeft','leftDown'],kLeft,kRight)              
                addConvectiveBC(A,b,nValues,DxAndDy,cellAreas,['rightDown'],kLeft,kRight,he,Te)



                

            if isMetalNode(i,j,MS_ids):    

                MSID,nMS_prev,nMS_next = getMetalNodesIDS(i,j,MS_ids,npy)

                
                currentPoint  = [ xMetal[MSID]  , yMetal[MSID] ]
                if (MSID>0):
                    previousPoint = [ xMetal[MSID-1], yMetal[MSID-1] ]

                if(MSID<nMSNodes-1):
                    nextPoint     = [ xMetal[MSID+1], yMetal[MSID+1] ]

                if MSID == 0:
                    
                    distanceToNext = dist(currentPoint,nextPoint)

                    A[n,n]        += -1*kMetal*eMetal/distanceToNext
                    A[n,nMS_next] += kMetal*eMetal/distanceToNext
                    
                elif MSID == nMSNodes -1:
                    
                    distanceToPrevious = dist(currentPoint,previousPoint)   
                    A[n,n] += -1*kMetal*eMetal/distanceToPrevious
                    A[n,nMS_prev] += kMetal*eMetal/distanceToPrevious
                
                else:
                    distanceToNext = dist(currentPoint,nextPoint)
                    distanceToPrevious = dist(currentPoint,previousPoint)   
    
                    A[n,nMS_prev] += kMetal*eMetal/distanceToPrevious
                    A[n,nMS_next] += kMetal*eMetal/distanceToNext
                    A[n,n] += -kMetal*eMetal*(1/distanceToPrevious + 1/distanceToNext)
            

            
    T = np.linalg.solve(A, b)
    

    heatFlux = computeWallHeatFlux(T,yticks,hi,Ti)

        
    
    metalProps = {'kMetal':kMetal,'eMetal':eMetal,'entreAxe':entreAxe}   
    boundaryConditions={'Ti':Ti,'Te':Te,'hi':hi,'he':he}
    RvaluesDict = computeUandRValues(heatFlux,metalProps,boundaryConditions,npy,T,npoints,eIsol,kIsol,Xuns,Yuns)

    
    return [Xuns,Yuns,T,RvaluesDict]

def computeWallHeatFlux(T,yticks,hi,Ti):
    
    npy = len(yticks)
    
    heatFlux = 0
    totalLenght= 0 
    for interval in range(1,npy):
        intervalLength = yticks[interval]-yticks[interval-1]
        intervalMeanT   = (T[interval]+T[interval-1])/2       #the N first nodes are the left bc
        intervalFlux   = hi*(Ti-intervalMeanT)*intervalLength

        totalLenght +=intervalLength
        heatFlux += intervalFlux


    return heatFlux
    

def addConductionFlux(A,b,nValues,DxAndDy, cellAreas,fluxes,kLeft,kRight):

        dxLeft,dxRight,dyUp,dyDown = DxAndDy                   
        AUpDownLeft,AUpDownRight,ALeftRightDown,ALeftRightUp = cellAreas

        n,nLeft,nRight,nDown,nUp = nValues

        for flux in fluxes:
            
            if flux=='upRight':
                upRight = kRight*AUpDownRight/dyUp

                A[n,n] += -upRight
                A[n,nUp] += upRight
                
            elif flux=='upLeft':            
                upLeft  = kLeft*AUpDownLeft/dyUp
                A[n,n] += -upLeft
                A[n,nUp] += upLeft

            if flux=='downRight':
                downRight = kRight*AUpDownRight/dyDown

                A[n,n] += -downRight
                A[n,nDown] += downRight
                
            if flux=='downLeft':            
                downLeft  = kLeft*AUpDownLeft/dyDown
                A[n,n] += -downLeft
                A[n,nDown] += downLeft

            if flux=='rightUp':
                rightUp   = kRight*ALeftRightUp/dxRight

                A[n,n] += -rightUp
                A[n,nRight] += rightUp

            if flux=='rightDown':
                rightDown   = kRight*ALeftRightDown/dxRight

                A[n,n] += -rightDown
                A[n,nRight] += rightDown


            if flux=='leftUp':
                leftUp   = kLeft*ALeftRightUp/dxLeft

                A[n,n] += -leftUp
                A[n,nLeft] += leftUp

            if flux=='leftDown':
                leftDown   = kLeft*ALeftRightDown/dxLeft

                A[n,n] += -leftDown
                A[n,nLeft] += leftDown



def addConvectiveFlux(A,b,nValues,DxAndDy, cellAreas,fluxes,kLeft,kRight,hValue):

        dxLeft,dxRight,dyUp,dyDown = DxAndDy                   
        AUpDownLeft,AUpDownRight,ALeftRightDown,ALeftRightUp = cellAreas

        n,nLeft,nRight,nDown,nUp = nValues

        for flux in fluxes:

            if flux=='rightUp':
                rightUp   = hValue*ALeftRightUp
                A[n,n] += -rightUp
                A[n,nRight] += rightUp

            if flux=='rightDown':
                rightDown = hValue*ALeftRightDown
                A[n,n] += -rightDown
                A[n,nRight] += rightDown


            if flux=='leftUp':
                leftUp   = hValue*ALeftRightUp
                A[n,n] += -leftUp
                A[n,nLeft] += leftUp

            if flux=='leftDown':
                leftDown   = hValue*ALeftRightDown
                A[n,n] += -leftDown
                A[n,nLeft] += leftDown


        

def addConvectiveBC(A,b,nValues,DxAndDy, cellAreas,fluxes,kLeft,kRight,hc,Tb):

        dxLeft,dxRight,dyUp,dyDown = DxAndDy                   
        AUpDownLeft,AUpDownRight,ALeftRightDown,ALeftRightUp = cellAreas

        n,nLeft,nRight,nDown,nUp = nValues

        for flux in fluxes:
            
            
            if (flux=='leftUp'):
                
                A[n,n] += -hc*ALeftRightUp #convective
                b[n]   += -hc*Tb*ALeftRightUp

            if (flux=='leftDown'):

                A[n,n] += -hc*ALeftRightDown #convective
                b[n]   += -hc*Tb*ALeftRightDown
    
            if (flux=='rightUp'):
                
                A[n,n] += -hc*ALeftRightUp #convective
                b[n]   += -hc*Tb*ALeftRightUp

            if (flux=='rightDown'):

                A[n,n] += -hc*ALeftRightDown #convective
                b[n]   += -hc*Tb*ALeftRightDown

    


def getNodeAndNeighbours(i,j,npx,npy):
    
    nLeft = nRight = nUp = nDown = np.nan
           
    
    n = getGlobalNodeNumber(i,j,npy)
    if (i>0):
        nLeft  = getGlobalNodeNumber(i-1,j,npy)
    if (i<npx-1):
        nRight = getGlobalNodeNumber(i+1,j,npy)
            
    if (j>0):
        nDown = getGlobalNodeNumber(i,j-1,npy)
    if (j<npy-1):
        nUp   = getGlobalNodeNumber(i,j+1,npy)

    return n,nLeft,nRight,nDown,nUp
    
    



def getMetalNodesIDS(i,j,MS_ids,npy):
    
    MSID = MS_ids[i,j] #ID of METAL STUD ELEMENTS, in their locl system 
    nMS_prev = getPrevMSnode(i,j,MS_ids,npy) #previous node ID in global system
    nMS_next = getNextMSnode(i,j,MS_ids,npy) #next node ID in global system"""
       
    return MSID,nMS_prev,nMS_next



def dist(p1,p2):
    
    return np.sqrt( (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2 )


def computeUandRValues(heatFlux,metalProps,boundaryConditions,ndy,T,npoints,eIsol,kIsol,Xuns,Yuns):
    
    
    Rsi = 1/boundaryConditions['hi']
    Rse = 1/boundaryConditions['he']
    

    Uglobal = heatFlux/metalProps['entreAxe']/(boundaryConditions['Ti']-boundaryConditions['Te'])
    Rglobal = 1/Uglobal
    
    RLayer = Rglobal - Rsi - Rse
    ULayer = 1/RLayer
    

    R2 = np.sum(np.array(eIsol)/np.array(kIsol)) # sum of e/lambda
    R1 = R2 + Rsi + Rse                          # incl Rsi and Rse
    R3 = Rglobal                                 # R with metal,, incl Rsi and Rse
    R4 = RLayer                                  # R with metal, solid layers only
    
    print('Unperturbed R-value ',np.round(R2,2),'W/m²K')
    print('R value ',np.round(RLayer,2),'m²K/W')   
    print('U value ',np.round(ULayer,2),'W/m²K')   
    
    return {'R1':R1,
            'R2':R2,
            'R3':R3,
            'R4':R4
            }

    
def getDxDy(xticks,yticks,i,j):
    
    if (i>0):
        dxLeft = xticks[i]-xticks[i-1]
    else:
        dxLeft=0
    
    if (i<len(xticks)-1):        
        dxRight = xticks[i+1]-xticks[i]
    else:
        dxRight=0
        
    if (j>0):
        dyDown = yticks[j]-yticks[j-1]
    else:
        dyDown = 0

    if (j<len(yticks)-1):    
        dyUp = yticks[j+1]-yticks[j]
    else:
        dyUp = 0
        
    return dxLeft,dxRight,dyUp,dyDown

def getCellAreas(xticks,yticks,i,j):

    AUpDownLeft = AUpDownRight = ALeftRightUp = ALeftRightDown = 0
    
    if (i>0):    
        AUpDownLeft = 0.5*(xticks[i]-xticks[i-1])

    if (i<len(xticks)-1):
        AUpDownRight = 0.5*(xticks[i+1]-xticks[i])
        
    if (j>0):    
        ALeftRightDown = 0.5*(yticks[j]-yticks[j-1])

    if (j<len(yticks)-1):
        ALeftRightUp = 0.5*(yticks[j+1]-yticks[j])


    return AUpDownLeft,AUpDownRight,ALeftRightDown,ALeftRightUp

         

def mapMetalNodes(xticks,yticks,shape,wMetal,hMetal,pMetal):

  
    if (shape=='C-shape'):
        ids,nNodes,xMS,yMS = mapCShapeNodes(xticks,yticks,wMetal,hMetal,pMetal)
            
    elif (shape=='U-shape'):
        ids,nNodes,xMS,yMS = mapUShapeNodes(xticks,yticks,wMetal,hMetal,pMetal)

       
    return ids,nNodes,xMS,yMS



def mapUShapeNodes(xticks,yticks,wMetal,hMetal,pMetal):
    
        #Lets call it C-shape
    
    #This configuration
    #
    #              line1            
    #         *****************
    #         *                
    #         *                
    # line2   *                   
    #         *                
    #         *                
    #         * ***************
    #               line3
    
    entreAxe = np.max(yticks)
    npx = len(xticks)
    npy = len(yticks)
        
    # Line 1
    i1 = np.argwhere( (xticks >=  pMetal) &  (xticks <= pMetal + hMetal) ).flatten()
    i1 = np.flip(i1)

    #print(yticks,(entreAxe+wMetal)/2)
    j1 = np.argwhere( yticks == (entreAxe+wMetal)/2 ).flatten()[0]

    #line2    
    i2 = i1[-1]
    j2 = np.argwhere( ( yticks < (entreAxe+wMetal)/2 ) & ( yticks > (entreAxe-wMetal)/2 )  ).flatten()
    j2 = np.flip(j2)    

    #line 3
    i3 = np.flip(i1)
    j3 = np.argwhere( yticks == (entreAxe-wMetal)/2 ).flatten()[0]
    
    xMS=[]
    yMS=[]

    ids = np.zeros((npx,npy))-1 #matrix holding IDS of MS nodes
    ids = ids.astype(int)

    currentID = 0

    #line 1    
    for iValue in i1:

        jValue = j1
       
        xMS.append(xticks[iValue])        
        yMS.append(yticks[jValue])        

        ids[iValue,jValue] = currentID
        currentID+=1



    for jValue in j2:
        iValue = i2
        
        xMS.append(xticks[iValue])        
        yMS.append(yticks[jValue])        

        ids[iValue,jValue] = currentID
        currentID+=1


    for iValue in i3:
        jValue = j3
        
        xMS.append(xticks[iValue])        
        yMS.append(yticks[jValue])        

        ids[iValue,jValue] = currentID
        currentID+=1


    nNodes = len(i1)+len(j2)+len(i3)
                
    return ids,nNodes,xMS,yMS

    


def mapCShapeNodes(xticks,yticks,wMetal,hMetal,pMetal):

    #Lets call it C-shape
    
    #This configuration
    #
    #              line2            
    #         ******************
    #         *                *
    #         *                *
    # line1   *                *   line3
    #         *                *
    #         *                *
    #         *                *
    entreAxe = np.max(yticks)
    npx = len(xticks)
    npy = len(yticks)
        
    # Line 1
    i1 = np.argwhere(xticks==(pMetal)).flatten()[0]
    j1 = np.argwhere( (yticks >= (entreAxe-hMetal)/2) & (yticks <= (entreAxe+hMetal)/2) ).flatten()

    #line2    
    j2 = j1[-1]
    i2 = np.argwhere( (xticks>pMetal) & (xticks<pMetal+wMetal)).flatten()    

    #line 3
    j3 = np.flip(j1)
    i3 = np.argwhere (xticks == pMetal+wMetal).flatten()[0]

    
    xMS=[]
    yMS=[]

    ids = np.zeros((npx,npy))-1 #matrix holding IDS of MS nodes
    ids = ids.astype(int)

    currentID = 0

    #line 1    
    for jValue in j1:

        iValue = i1
       
        xMS.append(xticks[iValue])        
        yMS.append(yticks[jValue])        

        ids[iValue,jValue] = currentID
        currentID+=1



    for iValue in i2:
        jValue = j2
        
        xMS.append(xticks[iValue])        
        yMS.append(yticks[jValue])        

        ids[iValue,jValue] = currentID
        currentID+=1


    for jValue in j3:
        iValue = i3
        
        xMS.append(xticks[iValue])        
        yMS.append(yticks[jValue])        

        ids[iValue,jValue] = currentID
        currentID+=1


    nNodes = len(j1)+len(i2)+len(j3)
                
    return ids,nNodes,xMS,yMS



def getGlobalNodeNumber(i,j,ndy):
    
    return i*ndy + j
            

  
 
    
def computeNodesLeftAndRightConductivity(eIsol,kIsol,xticks):
    
    npx=len(xticks)
    #For each node layer i, retruns the conductivity of the left cell and the right cell

    xarray = np.array(xticks)
    
    kI=np.zeros((npx,2))+kIsol[0] #col 0: left value, col1: right value
    
    eCumulated=0
    previousPivot = 0

    for e,k in zip(eIsol,kIsol):

        eCumulated+=e

        iPivot = np.argwhere(xarray==eCumulated)[0][0] #i value where there is a switch of conductiviey

        kI[previousPivot+1:iPivot,0]=k
        kI[previousPivot:iPivot,1]=k
        kI[iPivot,0]=k
    
        previousPivot=iPivot

    kI[-1,1]=k
    
    return kI

def computeNodeType(eIsol,kIsol,airLayerPosition,xticks):

    
    #node types:
    # "Normal"
    # "AirLayerLeftBoundary"
    # "AirLayerFirstNodeAfterLeftBoundary"
    # "AirLayerRightboundary"
    # "AirLayerLastNodeBeforeRightBondary"
    # "SingleNodeBetweenBoundaries
    
    npx=len(xticks)
    xarray = np.array(xticks)


    eCumulated=0
    layerNumber=0

    nodeTypes = np.full(npx,"Normal",dtype='<U40')
    
    if (airLayerPosition==None):
        return nodeTypes

    for e,k in zip(eIsol,kIsol):

        eCumulated+=e

        iPivot = np.argwhere(xarray==eCumulated)[0][0] #i value where there is a switch of conductiviey

        if (layerNumber == airLayerPosition-1):
            nodeTypes[iPivot]   = "AirLayerLeftBoundary"
            nodeTypes[iPivot+1] = "AirLayerFirstNodeAfterLeftBoundary"
        
        elif (layerNumber == airLayerPosition):
            nodeTypes[iPivot]   = "AirLayerRightBoundary"

            if (nodeTypes[iPivot-1] == "Normal"):
                nodeTypes[iPivot-1] = "AirLayerLastNodeBeforeRightBoundary"
            elif (nodeTypes[iPivot-1] == "AirLayerFirstNodeAfterLeftBoundary"):
                nodeTypes[iPivot-1] = "SingleNodeBetweenBoundaries"



        layerNumber+=1            


    return nodeTypes


def isMetalNode(i,j,MSMatrix):
    
    if MSMatrix[i,j]>=0:
        return True
    else:
        return False
    

def getPrevMSnode(i,j,MSMatrix,ndy):
    
    nodeMSID = MSMatrix[i,j]    

    try:
        iprev,jprev= getMSNodeFromID(MSMatrix,nodeMSID-1)
        return getGlobalNodeNumber(iprev,jprev,ndy)
    
    except:
        return -1
    
def getNextMSnode(i,j,MSMatrix,ndy):

    
    nodeMSID = MSMatrix[i,j]    

    try:
        inext,jnext= getMSNodeFromID(MSMatrix,nodeMSID+1)

        return getGlobalNodeNumber(inext,jnext,ndy)
    
    except:
        return -1


def getMSNodeFromID(IDMatrix,searchedMSID):
   
    i,j = np.where(IDMatrix == searchedMSID)
    
    return i[0],j[0]


    
if __name__ == '__main__':
    #genMesh()


    kMetal = 50
    eMetal = 0.0
    entreAxe = 0.6
    pMetal = 0.03
    wMetal = 0.05
    hMetal = 0.05
    
    Ti=20
    Te=0
    hi=10000
    he=10000

    shape = 'C-shape'
    
    metalProps = {'kMetal':kMetal,'eMetal':eMetal,'entreAxe':entreAxe,'shape':shape,'pMetal':pMetal,'hMetal':hMetal,'wMetal':wMetal}   
    boundaryConditions={'Ti':Ti,'Te':Te,'hi':hi,'he':he}
    
    eIsol = [0.01,0.02,0.05,0.09,0.05]
    kIsol=[0.20,0.13,0.035,np.nan,1.5]
    
    #
    #X,Y,T,Rdict = multiLayer_hConv_MS(eIsol = eIsol,kIsol = kIsol , pMetal=pMetal , wMetal = wMetal, hMetal = hMetal, entreAxe = entreAxe,kMetal = kMetal, eMetal = eMetal, hi=hi, he=he, MStype=shape,Ti=Ti,Te=Te)

    X,Y,T,Rdict = MsSolver(eIsol = eIsol,
                               kIsol = kIsol , 
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

    #X,Y,T,Rdict = multiLayer_hConv_MS(eIsol = eIsol,kIsol = kIsol , pMetal=pMetal , wMetal = wMetal, hMetal = hMetal, entreAxe = entreAxe,kMetal = kMetal, eMetal = 0, hi=hi, he=he, MStype=shape,Ti=Ti,Te=Te,airLayerPosition=2)

