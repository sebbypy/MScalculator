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
    
    def __init__(self,*,eIsol = [0.2] , kIsol=[0.035], pMetal=0.0, wMetal = 0.05, hMetal = 0.05, entreAxe = 0.6, kMetal = 50, eMetal=6e-4, hi=10, he=10, MStype='U-shape',Ti=20,Te=0,ResistanceAirLayer=0.18):
        
        self.eIsol=eIsol
        self.pMetal=pMetal
        self.wMetal=wMetal
        self.entreAxe = entreAxe
        self.kMetal = kMetal
        self.eMetal = eMetal
        self.hMetal = hMetal
        self.MStype = MStype
        self.kIsol=kIsol


        self.hi = hi
        self.he = he
        self.Ti = Ti
        self.Te = Te
        
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
          
        self.MeshManager = Mesher(eIsol = self.eIsol,
                               pMetal = self.pMetal,
                               hMetal = self.hMetal,
                               wMetal = self.wMetal,
                               entreAxe = self.entreAxe,
                               MStype = self.MStype,
                               kIsol = self.kIsol)
        
        xticks,yticks = self.MeshManager.genMesh()
                
        self.xticks = xticks
        self.yticks = yticks        
        
        self.npx = len(xticks)
        self.npy = len(yticks)
        self.npoints = self.npx*self.npy
        

    def computeCellProperties(self):
        
        if np.nan in self.kIsol:       
            #it means it is an air layer
            self.airLayerPosition = self.kIsol.index(np.nan)
            self.kIsol[self.airLayerPosition] = 1000
        else:
            self.airLayerPosition = None
        
        kI = self.computeNodesNeighbourConductivity()
        
        if self.MStype == 'Wood-shape':
            self.woodConductivity(kI)
        
        else:

            MS_ids,nMSNodes,xMetal,yMetal = self.MeshManager.mapMetalNodes() # table that contains -1 if nothing special or a null or positive id  if MS
            self.numberOfMetalNodes = nMSNodes

        nodeTypes = self.computeNodeType()
        
        
        self.kI = kI
        self.nodeTypes = nodeTypes
    

    def getNeighbourConductivityValues(self,i,j):

        return {'topLeft':self.kI[i,j,0],'topRight':self.kI[i,j,1],'botLeft':self.kI[i,j,2],'botRight':self.kI[i,j,3]}
    

    def computeNodeType(self):
            
        #node types:
        # "Normal"
        # "AirLayerLeftBoundary"
        # "AirLayerFirstNodeAfterLeftBoundary"
        # "AirLayerRightboundary"
        # "AirLayerLastNodeBeforeRightBondary"
        # "SingleNodeBetweenBoundaries
        
        xarray = np.array(self.xticks)
    
    
        eCumulated=0
        layerNumber=0
    
        nodeTypes = np.full(self.npx,"Normal",dtype='<U40')
        
        if (self.airLayerPosition==None):
            return nodeTypes
    
        for e,k in zip(self.eIsol,self.kIsol):
    
            eCumulated+=e
    
            iPivot = np.argwhere(xarray==eCumulated)[0][0] #i value where there is a switch of conductiviey
    
            if (layerNumber == self.airLayerPosition-1):
                nodeTypes[iPivot]   = "AirLayerLeftBoundary"
                nodeTypes[iPivot+1] = "AirLayerFirstNodeAfterLeftBoundary"
            
            elif (layerNumber == self.airLayerPosition):
                nodeTypes[iPivot]   = "AirLayerRightBoundary"
    
                if (nodeTypes[iPivot-1] == "Normal"):
                    nodeTypes[iPivot-1] = "AirLayerLastNodeBeforeRightBoundary"
                elif (nodeTypes[iPivot-1] == "AirLayerFirstNodeAfterLeftBoundary"):
                    nodeTypes[iPivot-1] = "SingleNodeBetweenBoundaries"
    
    
    
            layerNumber+=1            
    
    
        return nodeTypes

    
    
        
    def computeNodesNeighbourConductivity(self):
               
        xarray = np.array(self.xticks)
        yarray = np.array(self.yticks)
        
        kI=np.zeros((self.npx,self.npy,4))+self.kIsol[0] #col 0: left value, col1: right value
        
        eCumulated=0
        previousPivot = 0
    
        for e,k in zip(self.eIsol,self.kIsol):
    
            eCumulated+=e
    
            iPivot = np.argwhere(xarray==eCumulated)[0][0] #i value where there is a switch of conductiviey
    
            kI[previousPivot+1:iPivot,:,0]=k
            kI[previousPivot:iPivot,:,1]=k
            kI[iPivot,:,0]=k
        
            previousPivot=iPivot
    
        kI[-1,:,1]=k
    
        #end of layer calc
    
        #0 : top left
        #1: top right
        #2: bot left
        #3: bot right

        kI[:,:,2] = kI[:,:,0] #if no wood: top left = bot left
        kI[:,:,3] = kI[:,:,1]# if no wood: top right = bot right

         
        return kI
    
        
    def woodConductivity(self,conductivityMatrix):
        
        lambdawood = 0.13
        
        xarray = np.array(self.xticks)
        yarray = np.array(self.yticks)
        
     
        iLeftWood  = np.argwhere(xarray==self.pMetal)[0][0]
        iRightWood = np.argwhere(xarray==self.pMetal+self.wMetal)[0][0]

        jTopWood  = np.argwhere(yarray==(self.entreAxe+self.hMetal)/2)[0][0]
        jBotWood = np.argwhere(yarray==(self.entreAxe-self.hMetal)/2 )[0][0]


        #corners
        conductivityMatrix[iLeftWood,jTopWood,3] = lambdawood
        conductivityMatrix[iRightWood,jTopWood,2] = lambdawood
        conductivityMatrix[iLeftWood,jBotWood,1] = lambdawood
        conductivityMatrix[iRightWood,jBotWood,0] = lambdawood
        
        
        #boundaries
        conductivityMatrix[iLeftWood,jBotWood+1:jTopWood,1] = lambdawood #left boudary --> wood on the right
        conductivityMatrix[iLeftWood,jBotWood+1:jTopWood,3] = lambdawood #left boudary --> wood on the right
        
        conductivityMatrix[iRightWood,jBotWood+1:jTopWood,0] = lambdawood #left boudary --> wood on the left
        conductivityMatrix[iRightWood,jBotWood+1:jTopWood,2] = lambdawood #left boudary --> wood on the left

        conductivityMatrix[iLeftWood+1:iRightWood,jBotWood,0] = lambdawood #left boudary --> wood on the top
        conductivityMatrix[iLeftWood+1:iRightWood,jBotWood,1] = lambdawood #left boudary --> wood on the top
        
        conductivityMatrix[iLeftWood+1:iRightWood,jTopWood,2] = lambdawood #left boudary --> wood on the left
        conductivityMatrix[iLeftWood+1:iRightWood,jTopWood,3] = lambdawood #left boudary --> wood on the left
       
        #core
        conductivityMatrix[iLeftWood+1:iRightWood,jBotWood+1:jTopWood,:] = lambdawood 
        

        return 

    



    def fillMatrices(self):
        
        
        self.A = np.zeros((self.npoints,self.npoints))
        self.b = np.zeros(self.npoints)
        self.T=np.zeros(self.npoints)

        #MS_ids,nMSNodes,xMetal,yMetal = mapMetalNodes(self.xticks,self.yticks,self.MStype,self.wMetal,self.hMetal,self.pMetal) # table that contains -1 if nothing special or a null or positive id  if MS
        
        hair= 1/(self.ResitanceAirLayer/2)

        for i in range(self.npx):
            
            for j in range(self.npy):
    
                n = self.MeshManager.getNodeGlobalID(i,j)
                neighbours = self.MeshManager.getNodeNeighbours(i,j) #its a dict

                nValues = neighbours.copy()
                nValues['n'] = n
                
                kValues = self.getNeighbourConductivityValues(i,j)
    
                
                DxAndDy = self.MeshManager.getDxDy(i,j)            
                cellAreas = self.MeshManager.getCellAreas(i,j)
    
                
                #hair= 20
                #case 1 : normal cell
                if (i>0 and j>0 and i<self.npx-1 and j<self.npy-1):
    
                    if self.nodeTypes[i] == "AirLayerLeftBoundary":
                       
                        self.addConductionFlux(nValues,DxAndDy,cellAreas,['downLeft','leftDown','leftUp','upLeft'],
                                           kValues)
                        
                        self.addConvectiveFlux(nValues,DxAndDy,cellAreas,['rightUp','rightDown'],
                                           hair)
                        
    
                    elif self.nodeTypes[i] == "AirLayerFirstNodeAfterLeftBoundary":
    
                        self.addConductionFlux(nValues,DxAndDy,cellAreas,['downRight','rightDown','rightUp','upRight'],
                                           kValues)
                        
                        self.addConvectiveFlux(nValues,DxAndDy,cellAreas,['leftUp','leftDown'],
                                           hair)
    
                        
                    elif self.nodeTypes[i] == "AirLayerLastNodeBeforeRightBoundary":
    
                        self.addConductionFlux(nValues,DxAndDy,cellAreas,['downLeft','leftDown','leftUp','upLeft'],
                                           kValues)
                        
                        self.addConvectiveFlux(nValues,DxAndDy,cellAreas,['rightUp','rightDown'],
                                           hair)
                        
    
                    elif self.nodeTypes[i] == "AirLayerRightBoundary":
    
                        self.addConductionFlux(nValues,DxAndDy,cellAreas,['downRight','rightDown','rightUp','upRight'],
                                           kValues)
                        
                        self.addConvectiveFlux(nValues,DxAndDy,cellAreas,['leftUp','leftDown'],
                                           hair)
    
    
                    else: #normal node
                     
                        self.addConductionFlux(nValues,DxAndDy,cellAreas,
                                          ['rightUp','rightDown',
                                           'downRight','downLeft',
                                           'leftDown','leftUp',
                                           'upLeft','upRight'],
                                           kValues)
                        
                
                #case 2: normal left BC
                if (i==0 and (j !=0 and j != self.npy-1)):
    
                    self.addConductionFlux(nValues,DxAndDy,cellAreas,
                                      ['rightUp','rightDown','upRight','downRight'],kValues)
    
                    self.addConvectiveBC(nValues,DxAndDy,cellAreas,
                                      ['leftUp','leftDown'],self.hi,self.Ti)
    
                #botm left 
                if (i==0 and j==0):
                    
                    self.addConductionFlux(nValues,DxAndDy,cellAreas,['upRight','rightUp'],kValues)              
                    self.addConvectiveBC(nValues,DxAndDy,cellAreas,['leftUp'],self.hi,self.Ti)
    
    
                #top left                
                if (i==0 and j==self.npy-1):
    
                    self.addConductionFlux(nValues,DxAndDy,cellAreas,['downRight','rightDown'],kValues)              
                    self.addConvectiveBC(nValues,DxAndDy,cellAreas,['leftDown'],self.hi,self.Ti)
    
    
                #case 2: normal right
                if (i== self.npx-1 and (j !=0 and j != self.npy-1)):
                
                    self.addConductionFlux(nValues,DxAndDy,cellAreas,
                                      ['leftUp','leftDown','upLeft','downLeft'],kValues)
    
                    self.addConvectiveBC(nValues,DxAndDy,cellAreas,['rightUp','rightDown'],self.he,self.Te)
    
                
                #case 4: normal bot: symmetric
                if (j== 0 and (i !=0 and i != self.npx-1)):
    
                    if self.nodeTypes[i] == "AirLayerLeftBoundary":
                        
                        self.addConductionFlux(nValues,DxAndDy,cellAreas,['upLeft','leftUp'],kValues)
                        self.addConvectiveFlux(nValues,DxAndDy,cellAreas,['rightUp'],hair)
    
                    elif self.nodeTypes[i] == "AirLayerFirstNodeAfterLeftBoundary":
                        
                        self.addConductionFlux(nValues,DxAndDy,cellAreas,['upLeft','upRight','rightUp'],kValues)
                        self.addConvectiveFlux(nValues,DxAndDy,cellAreas,['leftUp'],hair)
    
                    elif self.nodeTypes[i] == "AirLayerLastNodeBeforeRightBoundary":
                        
                        self.addConductionFlux(nValues,DxAndDy,cellAreas,['upLeft','upRight','leftUp'],kValues)                
                        self.addConvectiveFlux(nValues,DxAndDy,cellAreas,['rightUp'],hair)
    
                    elif self.nodeTypes[i] == "AirLayerRightBoundary":
    
                        self.addConductionFlux(nValues,DxAndDy,cellAreas,['upRight','rightUp'],kValues)                    
                        self.addConvectiveFlux(nValues,DxAndDy,cellAreas,['leftUp'],hair)
                        
    
                    else:               
                        self.addConductionFlux(nValues,DxAndDy,cellAreas,['rightUp','upRight','upLeft','leftUp'],kValues)
                    
    
                    
                #case 5: normal top: symmetric
                if (j== self.npy-1 and (i !=0 and i != self.npx-1)):
    
                    if self.nodeTypes[i] == "AirLayerLeftBoundary":
                        
                        self.addConductionFlux(nValues,DxAndDy,cellAreas,
                                           ['downLeft','leftDown'],
                                           kValues)
                        
                        self.addConvectiveFlux(nValues,DxAndDy,cellAreas,
                                           ['rightDown'],
                                           hair)
    
                    elif self.nodeTypes[i] == "AirLayerFirstNodeAfterLeftBoundary":
                        
                        self.addConductionFlux(nValues,DxAndDy,cellAreas,
                                           ['downLeft','downRight','rightDown'],
                                           kValues)
                        
                        self.addConvectiveFlux(nValues,DxAndDy,cellAreas,
                                           ['leftDown'],
                                           hair)
    
                    elif self.nodeTypes[i] == "AirLayerLastNodeBeforeRightBoundary":
                        
                        self.addConductionFlux(nValues,DxAndDy,cellAreas,
                                           ['downLeft','downRight','leftDown'],
                                           kValues)
                        
                        self.addConvectiveFlux(nValues,DxAndDy,cellAreas,
                                           ['rightDown'],
                                           hair)
    
                    elif self.nodeTypes[i] == "AirLayerRightBoundary":
    
                        self.addConductionFlux(nValues,DxAndDy,cellAreas,
                                           ['downRight','rightDown'],
                                           kValues)
                        
                        self.addConvectiveFlux(nValues,DxAndDy,cellAreas,
                                           ['leftDown'],
                                           hair)
                        
                    else:
                        self.addConductionFlux(nValues,DxAndDy,cellAreas,
                                          ['rightDown','downRight','downLeft','leftDown'],
                                           kValues)              
    
    
                #bot right                
                if (i==self.npx-1 and j==0):
    
                    self.addConductionFlux(nValues,DxAndDy,cellAreas,['upLeft','leftUp'],kValues)              
                    self.addConvectiveBC(nValues,DxAndDy,cellAreas,['rightUp'],self.he,self.Te)
    
                #top right
                if (i==self.npx-1 and j==self.npy-1):
                    
                    self.addConductionFlux(nValues,DxAndDy,cellAreas,['downLeft','leftDown'],kValues)              
                    self.addConvectiveBC(nValues,DxAndDy,cellAreas,['rightDown'],self.he,self.Te)
    
                
                if self.MStype in ['U-shape','C-shape']:
    
                    if self.MeshManager.isMetalNode(i,j):    
        
                        MSID = self.MeshManager.getCurrentNodeMetalID(i,j)
                        
                        nMS_next = self.MeshManager.getNextMetalNodeGlobalID(i,j)
                        nMS_prev = self.MeshManager.getPrevMetalNodeGlobalID(i,j)
    
        
                        if MSID == 0:
                            
                            distanceToNext = self.MeshManager.computeDistance(n,nMS_next)
        
                            self.A[n,n]        += -1*self.kMetal*self.eMetal/distanceToNext
                            self.A[n,nMS_next] += self.kMetal*self.eMetal/distanceToNext
                            
                        elif MSID == self.numberOfMetalNodes-1:
                            
                            distanceToPrevious = self.MeshManager.computeDistance(n,nMS_prev)
                            self.A[n,n] += -1*self.kMetal*self.eMetal/distanceToPrevious
                            self.A[n,nMS_prev] += self.kMetal*self.eMetal/distanceToPrevious
                        
                        else:
                            distanceToNext = self.MeshManager.computeDistance(n,nMS_next)
                            distanceToPrevious = self.MeshManager.computeDistance(n,nMS_prev)
            
                            self.A[n,nMS_prev] += self.kMetal*self.eMetal/distanceToPrevious
                            self.A[n,nMS_next] += self.kMetal*self.eMetal/distanceToNext
                            self.A[n,n] += -self.kMetal*self.eMetal*(1/distanceToPrevious + 1/distanceToNext)
            

    
    
    def addConductionFlux(self,nValues,DxAndDy, cellAreas,fluxes,kValues):

        
        
        
        dxLeft,dxRight,dyUp,dyDown = DxAndDy                   
        AUpDownLeft,AUpDownRight,ALeftRightDown,ALeftRightUp = cellAreas

        n = nValues['n']
        nLeft  = nValues['nLeft']
        nRight = nValues['nRight']
        nUp = nValues['nUp']
        nDown = nValues['nDown']


        for flux in fluxes:
            
            if flux=='upRight':
                upRight = kValues['topRight']*AUpDownRight/dyUp

                self.A[n,n] += -upRight
                self.A[n,nUp] += upRight
                
            elif flux=='upLeft':            
                upLeft  = kValues['topLeft']*AUpDownLeft/dyUp
                self.A[n,n] += -upLeft
                self.A[n,nUp] += upLeft

            if flux=='downRight':
                downRight = kValues['botRight']*AUpDownRight/dyDown

                self.A[n,n] += -downRight
                self.A[n,nDown] += downRight
                
            if flux=='downLeft':            
                downLeft  = kValues['botLeft']*AUpDownLeft/dyDown
                self.A[n,n] += -downLeft
                self.A[n,nDown] += downLeft

            if flux=='rightUp':
                rightUp   = kValues['topRight']*ALeftRightUp/dxRight

                self.A[n,n] += -rightUp
                self.A[n,nRight] += rightUp

            if flux=='rightDown':
                rightDown   = kValues['botRight']*ALeftRightDown/dxRight

                self.A[n,n] += -rightDown
                self.A[n,nRight] += rightDown


            if flux=='leftUp':
                leftUp   = kValues['topLeft']*ALeftRightUp/dxLeft

                self.A[n,n] += -leftUp
                self.A[n,nLeft] += leftUp

            if flux=='leftDown':
                leftDown   = kValues['botLeft']*ALeftRightDown/dxLeft

                self.A[n,n] += -leftDown
                self.A[n,nLeft] += leftDown


    def addConvectiveFlux(self,nValues,DxAndDy, cellAreas,fluxes, hValue):
        
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
            

    def addConvectiveBC(self,nValues,DxAndDy, cellAreas,fluxes,hc,Tb):

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
                
                n = self.MeshManager.getNodeGlobalID(i,j)
                
                Xuns[n] = self.xticks[i]
                Yuns[n] = self.yticks[j]
        

        return Xuns,Yuns        


class Mesher:
    
    def __init__(self,*,eIsol,pMetal,wMetal,hMetal,entreAxe,MStype,kIsol):

        self.eIsol=eIsol
        self.pMetal=pMetal
        self.wMetal=wMetal
        self.entreAxe = entreAxe
        self.hMetal = hMetal
        self.MStype = MStype
        self.kIsol=kIsol


    def genMesh(self):
        
          #def genMesh(*,eIsol,pMetal,wMetal,hMetal,shape,entreAxe):
    
        sizeMS = 5e-3
        sizeOther = 2e-2
        
        
        if self.MStype=='C-shape' or 'Wood-shape':
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
        self.noints = self.npx*self.npy
        
        return xticks,yticks
    
    
    def mapMetalNodes(self):
  
        if (self.MStype=='C-shape'):
            ids,nNodes,xMS,yMS = self.mapCShapeNodes()
                
        elif (self.MStype=='U-shape'):
            ids,nNodes,xMS,yMS = self.mapUShapeNodes()
    
        self.MetalNodesIdMatrix = ids
           
        return ids,nNodes,xMS,yMS



    def mapUShapeNodes(self):
        
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
        
            
        # Line 1
        i1 = np.argwhere( (self.xticks >=  self.pMetal) &  (self.xticks <= self.pMetal + self.hMetal) ).flatten()
        i1 = np.flip(i1)
    
        #print(yticks,(self.entreAxe+self.wMetal)/2)
        j1 = np.argwhere( self.yticks == (self.entreAxe+self.wMetal)/2 ).flatten()[0]
    
        #line2    
        i2 = i1[-1]
        j2 = np.argwhere( ( self.yticks < (self.entreAxe+self.wMetal)/2 ) & ( self.yticks > (self.entreAxe-self.wMetal)/2 )  ).flatten()
        j2 = np.flip(j2)    
    
        #line 3
        i3 = np.flip(i1)
        j3 = np.argwhere( self.yticks == (self.entreAxe-self.wMetal)/2 ).flatten()[0]
        
        xMS=[]
        yMS=[]
    
        ids = np.zeros((self.npx,self.npy))-1 #matrix holding IDS of MS nodes
        ids = ids.astype(int)
    
        currentID = 0
    
        #line 1    
        for iValue in i1:
    
            jValue = j1
           
            xMS.append(self.xticks[iValue])        
            yMS.append(self.yticks[jValue])        
    
            ids[iValue,jValue] = currentID
            currentID+=1
    
    
    
        for jValue in j2:
            iValue = i2
            
            xMS.append(self.xticks[iValue])        
            yMS.append(self.yticks[jValue])        
    
            ids[iValue,jValue] = currentID
            currentID+=1
    
    
        for iValue in i3:
            jValue = j3
            
            xMS.append(self.xticks[iValue])        
            yMS.append(self.yticks[jValue])        
    
            ids[iValue,jValue] = currentID
            currentID+=1
    
    
        nNodes = len(i1)+len(j2)+len(i3)
                    
        return ids,nNodes,xMS,yMS
    
        
    
    
    def mapCShapeNodes(self):
    
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
            
        # Line 1
        i1 = np.argwhere(self.xticks==(self.pMetal)).flatten()[0]
        j1 = np.argwhere( (self.yticks >= (self.entreAxe-self.hMetal)/2) & (self.yticks <= (self.entreAxe+self.hMetal)/2) ).flatten()
    
        #line2    
        j2 = j1[-1]
        i2 = np.argwhere( (self.xticks > self.pMetal) & (self.xticks < self.pMetal + self.wMetal)).flatten()    
    
        #line 3
        j3 = np.flip(j1)
        i3 = np.argwhere (self.xticks == self.pMetal+self.wMetal).flatten()[0]
    
        
        xMS=[]
        yMS=[]
    
        ids = np.zeros((self.npx,self.npy))-1 #matrix holding IDS of MS nodes
        ids = ids.astype(int)
    
        currentID = 0
    
        #line 1    
        for jValue in j1:
    
            iValue = i1
           
            xMS.append(self.xticks[iValue])        
            yMS.append(self.yticks[jValue])        
    
            ids[iValue,jValue] = currentID
            currentID+=1
    
    
    
        for iValue in i2:
            jValue = j2
            
            xMS.append(self.xticks[iValue])        
            yMS.append(self.yticks[jValue])        
    
            ids[iValue,jValue] = currentID
            currentID+=1
    
    
        for jValue in j3:
            iValue = i3
            
            xMS.append(self.xticks[iValue])        
            yMS.append(self.yticks[jValue])        
    
            ids[iValue,jValue] = currentID
            currentID+=1
    
    
        nNodes = len(j1)+len(i2)+len(j3)
                    
        return ids,nNodes,xMS,yMS
    

    def isMetalNode(self,i,j):
        
        
        if self.MetalNodesIdMatrix[i,j]>=0:
            return True
        else:
            return False
        
    def getCurrentNodeMetalID(self,i,j):
        
        return self.MetalNodesIdMatrix[i,j]
        
    
    def getPrevMetalNodeGlobalID(self,i,j):
        
        nodeMSID = self.MetalNodesIdMatrix[i,j]    
    
        try:
            iprev,jprev= self.getIJFromLocalID(nodeMSID-1)
            return self.getNodeGlobalID(iprev,jprev)
        
        except:
            return -1
        
    def getNextMetalNodeGlobalID(self,i,j):
    
        nodeMSID = self.MetalNodesIdMatrix[i,j]    
    
        try:
            inext,jnext= self.getIJFromLocalID(nodeMSID+1)
    
            return self.getNodeGlobalID(inext,jnext)
        
        except:
            return -1
    
    
    def getIJFromLocalID(self,searchedMetalNodeId):
       
        i,j = np.where(self.MetalNodesIdMatrix == searchedMetalNodeId)
        
        
        return i[0],j[0]
       
    
    def getNodeNeighbours(self,i,j):
        
        nLeft = nRight = nUp = nDown = np.nan
        
        if (i>0):
            nLeft  = self.getNodeGlobalID(i-1,j)
        if (i<self.npx-1):
            nRight = self.getNodeGlobalID(i+1,j)
                
        if (j>0):
            nDown = self.getNodeGlobalID(i,j-1)
        if (j<self.npy-1):
            nUp   = self.getNodeGlobalID(i,j+1)
    
        return {'nLeft':nLeft,'nRight':nRight,'nDown':nDown,'nUp':nUp}

    
    def getNodeGlobalID(self,i,j):
    
        return i*self.npy + j

    def getIJFromGlobalID(self,n):
        
        i = int(n/self.npy)
        j = n%self.npy
        
        return i,j


    def getDxDy(self,i,j):
        
        if (i>0):
            dxLeft = self.xticks[i]-self.xticks[i-1]
        else:
            dxLeft=0
        
        if (i<len(self.xticks)-1):        
            dxRight = self.xticks[i+1]-self.xticks[i]
        else:
            dxRight=0
            
        if (j>0):
            dyDown = self.yticks[j]-self.yticks[j-1]
        else:
            dyDown = 0
    
        if (j<len(self.yticks)-1):    
            dyUp = self.yticks[j+1]-self.yticks[j]
        else:
            dyUp = 0
            
        return dxLeft,dxRight,dyUp,dyDown
    
    def getCellAreas(self,i,j):
    
        AUpDownLeft = AUpDownRight = ALeftRightUp = ALeftRightDown = 0
        
        if (i>0):    
            AUpDownLeft = 0.5*(self.xticks[i]-self.xticks[i-1])
    
        if (i<len(self.xticks)-1):
            AUpDownRight = 0.5*(self.xticks[i+1]-self.xticks[i])
            
        if (j>0):    
            ALeftRightDown = 0.5*(self.yticks[j]-self.yticks[j-1])
    
        if (j<len(self.yticks)-1):
            ALeftRightUp = 0.5*(self.yticks[j+1]-self.yticks[j])
    
    
        return AUpDownLeft,AUpDownRight,ALeftRightDown,ALeftRightUp


    
         
    def computeDistance(self,node1Id,node2Id):
                
        
        i1,j1 = self.getIJFromGlobalID(node1Id)
        i2,j2 = self.getIJFromGlobalID(node2Id)
        
        
        x1 = self.xticks[i1]
        x2 = self.xticks[i2]

        y1 = self.yticks[j1]
        y2 = self.yticks[j2]
        
        return np.sqrt( (x1-x2)**2 + (y1-y2)**2 )
        



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

    
 
    
if __name__ == '__main__':
    #genMesh()


    kMetal = 50
    eMetal = 6e-4
    entreAxe = 0.6
    pMetal = 0.03
    wMetal = 0.05
    hMetal = 0.05
    
    Ti=20
    Te=0
    hi=10
    he=10

    shape = 'C-shape'
    
    metalProps = {'kMetal':kMetal,'eMetal':eMetal,'entreAxe':entreAxe,'shape':shape,'pMetal':pMetal,'hMetal':hMetal,'wMetal':wMetal}   
    boundaryConditions={'Ti':Ti,'Te':Te,'hi':hi,'he':he}
    
    eIsol = [0.01,0.02,0.05,0.09,0.05]
    kIsol=[0.20,0.13,0.035,0.035,1.5]
    
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

