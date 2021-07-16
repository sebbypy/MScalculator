# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 09:35:28 2021

@author: spec
"""

#METAL STUD 2d SOLVER

import numpy as np
    
#Non uniform version to have an automatic mesh with variable step size. 

#Imagined mesh rules:
# max .5 cm on an area of twice the size of the MS profile
# 1 cm elsewhere or even more in the X direct
# handle mm thickness. 


# Steps to implement
# define a variable size mesh
# revise the A-Matrix coefficients to handle the variable mesh size


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
    xticks.append(pMetal+wMetal)

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
    xticks.append(pMetal+wMetal)

    
    xticks = list(set(xticks))
    xticks.sort()    
    xticks = refineGloballyX(xticks,size)


    #yticks management
    yticks = [0,
              entreAxe/2-hMetal/2,
              entreAxe/2+hMetal/2,
              entreAxe
              ]
    yticks = refineGloballyX(yticks,size)
    
    
    return [xticks,yticks]



def refineGloballyX(inputTicks,maxdx):
   
    pointsToAdd=[]
    
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


def multiLayer_hConv_MS(*,eIsol = [0.2] , kIsol=[0.035], pMetal=0.0, wMetal = 0.05, hMetal = 0.05, entreAxe = 0.6, kMetal = 50, eMetal=6e-4, hi=10, he=10, MStype='U-shape',Ti=20,Te=0,mesh='nonuniform'):

    if mesh == 'nonuniform':
    
        xticks,yticks = genMesh(eIsol=eIsol,pMetal=pMetal,wMetal=wMetal,hMetal=hMetal,entreAxe=entreAxe,shape=MStype)

    else:
        xticks,yticks = genUniformMesh(eIsol=eIsol,pMetal=pMetal,wMetal=wMetal,hMetal=hMetal,entreAxe=entreAxe,shape=MStype)

    xticks=np.array(xticks)
    yticks=np.array(yticks)
    
    npx = len(xticks)
    npy = len(yticks)
    
    npoints = npx*npy


    kI = computeNodesLeftAndRightConductivity(eIsol,kIsol,xticks)

    MS_ids,nMSNodes,xMetal,yMetal = mapMetalNodes(xticks,yticks,MStype,wMetal,hMetal,pMetal) # table that contains -1 if nothing special or a null or positive id  if MS


    A = np.zeros((npoints,npoints))
    b = np.zeros(npoints)
    T=np.zeros(npoints)
    
    #Unstructured coordinates
    Xuns=np.zeros(npoints)
    Yuns=np.zeros(npoints)
    
    
    for i in range(npx):
        
        for j in range(npy):

            nLeft = nRight = nUp = nDown = np.nan
            
            if isMetalNode(i,j,MS_ids):
    
                MSID = MS_ids[i,j] #ID of METAL STUD ELEMENTS, in their locl system 
                nMS_prev = getPrevMSnode(i,j,MS_ids,npy) #previous node ID in global system
                nMS_next = getNextMSnode(i,j,MS_ids,npy) #next node ID in global system"""
                            
            n = getGlobalNodeNumber(i,j,npy)

            Xuns[n] = xticks[i]
            Yuns[n] = yticks[j]
            
            if (i>0):
                nLeft  = getGlobalNodeNumber(i-1,j,npy)
            if (i<npx-1):
                nRight = getGlobalNodeNumber(i+1,j,npy)
            
            if (j>0):
                nDown = getGlobalNodeNumber(i,j-1,npy)
            if (j<npy-1):
                nUp   = getGlobalNodeNumber(i,j+1,npy)

            kLeft  = kI[i,0]
            kRight = kI[i,1]

            
            dxLeft,dxRight,dyUp,dyDown = getDxDy(xticks,yticks,i,j)            
            AUpDownLeft,AUpDownRight,ALeftRightDown,ALeftRightUp = getCellAreas(xticks,yticks,i,j)

            

            ALeftRight = ALeftRightUp + ALeftRightDown #whole area for inner cell

            #case 1 : normal cell
            if (i>0 and j>0 and i<npx-1 and j<npy-1):
                               
                A[n,n] = -(kLeft/dxLeft + kRight/dxRight) * ALeftRight - (1/dyUp + 1/dyDown)*( kLeft*AUpDownLeft +kRight*AUpDownRight)
                A[n,nLeft]  = kLeft/dxLeft*ALeftRight
                A[n,nRight] = kRight/dxRight*ALeftRight
                A[n,nDown]  = (1/dyDown)* ( kLeft*AUpDownLeft +kRight*AUpDownRight)
                A[n,nUp]    = (1/dyUp)  * ( kLeft*AUpDownLeft +kRight*AUpDownRight)
                b[n] = 0
            
            #case 2: normal left BC
            if (i==0 and (j !=0 and j != npy-1)):

                A[n,n] = -(kRight/dxRight) * ALeftRight - (1/dyUp + 1/dyDown)*(kRight*AUpDownRight)
                A[n,nRight] = kRight/dxRight*ALeftRight
                A[n,nDown]  = (1/dyDown)* (kRight*AUpDownRight)
                A[n,nUp]    = (1/dyUp)  * (kRight*AUpDownRight)
                b[n] = 0

                A[n,n] += -hi*ALeftRight #convective
                b[n] = -hi*Ti*ALeftRight

            #botm left 
            if (i==0 and j==0):
                A[n,n] = -(kRight/dxRight) * ALeftRightUp #- (1/dyUp)*(kRight*AUpDownRight)
                A[n,nRight] = kRight/dxRight*ALeftRightUp
                b[n] = 0

                A[n,n] += -hi*ALeftRightUp #convective
                b[n]    = -hi*Ti*ALeftRightUp

            #top left                
            if (i==0 and j==npy-1):
                A[n,n] = -(kRight/dxRight) * ALeftRightDown #- (1/dyDown)*(kRight*AUpDownRight)
                A[n,nRight] = kRight/dxRight*ALeftRightDown
                b[n] = 0

                A[n,n] += -hi*ALeftRightDown #convective
                b[n]    = -hi*Ti*ALeftRightDown

            #case 2: normal right
            if (i== npx-1 and (j !=0 and j != npy-1)):

                A[n,n] = -(kLeft/dxLeft) * ALeftRight - (1/dyUp + 1/dyDown)*(kLeft*AUpDownLeft)
                A[n,nLeft] = kLeft/dxLeft*ALeftRight
                A[n,nDown]  = (1/dyDown)* (kLeft*AUpDownLeft)
                A[n,nUp]    = (1/dyUp)  * (kLeft*AUpDownLeft)
                b[n] = 0

                A[n,n] += -he*ALeftRight #convective
                b[n] = -he*Te*ALeftRight
            
            #case 4: normal bot: symmetric
            if (j== 0 and (i !=0 and i != npx-1)):

                A[n,n] = -(kLeft/dxLeft + kRight/dxRight) * ALeftRightUp
                A[n,nLeft]  = kLeft/dxLeft*ALeftRightUp
                A[n,nRight] = kRight/dxRight*ALeftRightUp
                #A[n,nUp]    = (1/dyUp)  * ( kLeft*AUpDownLeft +kRight*AUpDownRight)

                b[n] = 0
                
            #case 5: normal top: symmetric
            if (j== npy-1 and (i !=0 and i != npx-1)):

                A[n,n] = -(kLeft/dxLeft + kRight/dxRight) * ALeftRightDown
                A[n,nLeft]  = kLeft/dxLeft*ALeftRightDown
                A[n,nRight] = kRight/dxRight*ALeftRightDown
                #A[n,nDown]  = (1/dyDown)* ( kLeft*AUpDownLeft +kRight*AUpDownRight)

                b[n] = 0

            #bot right                
            if (i==npx-1 and j==0):

                A[n,n] = -(kLeft/dxLeft) * ALeftRightUp #- (1/dyUp)*(kLeft*AUpDownLeft)
                A[n,nLeft] = kLeft/dxLeft*ALeftRightUp
                b[n] = 0

                A[n,n] += -he*ALeftRightUp #convective
                b[n]    = -he*Te*ALeftRightUp

            #top right
            if (i==npx-1 and j==npy-1):
                
                
                A[n,n] = -(kLeft/dxLeft) * ALeftRightDown #- (1/dyDown)*(kLeft*AUpDownLeft)
                A[n,nLeft] = kLeft/dxLeft*ALeftRightDown
                b[n] = 0

                A[n,n] += -he*ALeftRightDown #convective
                b[n]    = -he*Te*ALeftRightDown

                

            if isMetalNode(i,j,MS_ids):    
               
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
            

    #np.set_printoptions(threshold=sys.maxsize)
    #print(A)    
    
    np.savetxt('non-uniforma.csv',A,delimiter=',',fmt='%10.4f')
    np.savetxt('non-uniformb.csv',b,delimiter=',',fmt='%10.4f')

            
    T = np.linalg.solve(A, b)
    

    heatFlux = 0
    totalLenght= 0 
    for interval in range(1,npy):
        intervalLength = yticks[interval]-yticks[interval-1]
        intervalMeanT   = (T[interval]+T[interval-1])/2       #the N first nodes are the left bc
        intervalFlux   = hi*(Ti-intervalMeanT)*intervalLength

        totalLenght +=intervalLength
        heatFlux += intervalFlux


    #heatFlux = -entreAxe*hi*(np.mean(T[range(npy)])-Ti) # i = 0 
    #// should be equal print(entreAxe*he*(np.mean(T[range(npoints-npy,npoints)])-Te))
        
    
    metalProps = {'kMetal':kMetal,'eMetal':eMetal,'entreAxe':entreAxe}   
    boundaryConditions={'Ti':Ti,'Te':Te,'hi':hi,'he':he}
    RvaluesDict = computeUandRValues(heatFlux,metalProps,boundaryConditions,npy,T,npoints,eIsol,kIsol,Xuns,Yuns)

    
    return [Xuns,Yuns,T,RvaluesDict]
    

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


