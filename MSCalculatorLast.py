# -*- coding: utf-8 -*-
'''
Éditeur de Spyder

Ceci est un script temporaire.
'''

#METAL STUD 2d SOLVER

import matplotlib.pyplot as plt
import numpy as np


def main():

    plt.close('all')
    
        
    multiLayer_hConv_MS(eIsol=[0.01,0.01,0.05,0.01],
                        kIsol=[0.20,0.13,0.035,0.13], 
                        pMetal=0.02, 
                        wMetal = 0.05, 
                        hMetal=0.03, 
                        dx=0.005, 
                        MStype='U-shape',
                        plot=True)

    multiLayer_hConv_MS(eIsol=[0.01,0.01,0.05,0.01],
                        kIsol=[0.20,0.13,0.035,0.13], 
                        pMetal=0.02, 
                        wMetal = 0.05, 
                        hMetal=0.03, 
                        dx=0.005, 
                        MStype='C-shape',
                        plot=True)
    

def multiLayer_hConv_MS(*,eIsol = [0.01,0.02,0.1] , kIsol=[0.20,0.13,0.035], pMetal=0.03, wMetal = 0.05, hMetal = 0.05, entreAxe = 0.6,dx = 5e-3 ,kMetal = 50, eMetal=6e-4, hi=10, he=10, MStype='U-shape',plot=True):

    #eIsol: list of layers thickness
    #kIsol: list of layers lambda
    #pMetal = postiion of the metal from inside (cm)
        
    dy = dx        
    
    Te=0
    Ti=20
    
    ndx = int(np.sum(eIsol)/dx)+1
    ndy= int(entreAxe/dy)+1
    npoints = ndx*ndy

    kI = computeNodesLeftAndRightConductivity(eIsol,kIsol,dx,ndx)


    #
    #if MStype == 'U-shape':
    MS_ids,nMSNodes,xMetal,yMetal = mapMetalNodes(ndx,ndy,dx,MStype,wMetal,hMetal,pMetal) # table that contains -1 if nothing special or a null or positive id  if MS
    #else:
    #    MS_ids,nMSNodes = compute_MS_ids(ndx,ndy,dx,wMetal,hMetal,pMetal) # table that contains -1 if nothing special or a null or positive id  if MS


    #Definition of linear system Matrix
    A = np.zeros((npoints,npoints))
    b = np.zeros(npoints)
    T=np.zeros(npoints)
    
    #Unstructured coordinates
    Xuns=np.zeros(npoints)
    Yuns=np.zeros(npoints)
    
    
    for i in range(ndx):
        for j in range(ndy):

            
            if isMetalNode(i,j,MS_ids):
    
                MSID = MS_ids[i,j] #ID of METAL STUD ELEMENTS, in their locl system 
                nMS_prev = getPrevMSnode(i,j,MS_ids,ndy) #previous node ID in global system
                nMS_next = getNextMSnode(i,j,MS_ids,ndy) #next node ID in global system
                            
            n = getGlobalNodeNumber(i,j,ndy)

            Xuns[n] = i*dx
            Yuns[n] = j*dy
            
            nLeft  = getGlobalNodeNumber(i-1,j,ndy)
            nRight = getGlobalNodeNumber(i+1,j,ndy)
            
            nDown = getGlobalNodeNumber(i,j-1,ndy)
            nUp   = getGlobalNodeNumber(i,j+1,ndy)

            kLeft  = kI[i,0]
            kRight = kI[i,1]
            

            #case 1 : normal cell
            if (i>0 and j>0 and i<ndx-1 and j<ndy-1):
                               
                A[n,n] = -(kLeft+kRight)/dx**2 - (kLeft+kRight)/dy**2
                A[n,nLeft] = kLeft/dx**2
                A[n,nRight] = kRight/dx**2
                A[n,nDown] = (kLeft+kRight)/2/dy**2
                A[n,nUp] = (kLeft+kRight)/2/dy**2
                b[n] = 0
            
            #case 2: normal left BC
            if (i==0 and (j !=0 and j != ndy-1)):
               
                A[n,n] = -kRight/dx**2 - 2*kRight/dy**2/2
                A[n,nRight] = kRight/dx**2
 
                A[n,nDown] = kRight/dy**2/2
                A[n,nUp] = kRight/dy**2/2

                A[n,n] += -hi/dx #convective
                b[n] = -hi*Ti/dx

            #botm left 
            if (i==0 and j==0):

                A[n,n] = -kRight/dx**2/2 #- 2/dy**2/2
                A[n,nRight] = kRight/dx**2/2
                
                A[n,n] += -hi/dx/2
                b[n] = -hi*Ti/dx/2

            #top left                
            if (i==0 and j==ndy-1):

                A[n,n] = -kRight/dx**2/2 
                A[n,nRight] = kRight/dx**2/2

                A[n,n] += -hi/dx/2
                b[n] = -hi*Ti/dx/2

            #case 2: normal right
            if (i== ndx-1 and (j !=0 and j != ndy-1)):
                
                A[n,n] = -kLeft/dx**2 - 2*kLeft/dy**2/2
                A[n,nLeft] = kLeft/dx**2
                A[n,nDown] = kLeft/dy**2/2
                A[n,nUp] = kLeft/dy**2/2

                A[n,n] += -he/dx #convective
                b[n] = -he*Te/dx

            
            #case 4: normal top: symmetric
            if (j== 0 and (i !=0 and i != ndx-1)):
                
                A[n,n] = -(kLeft+kRight)/dx**2/2 
                A[n,nRight] = kRight/dx**2/2
                A[n,nLeft] = kLeft/dx**2/2
                b[n] = 0
                
            #case 5: normal bot: symmetric
            if (j== ndy-1 and (i !=0 and i != ndx-1)):
                
                A[n,n] = -(kLeft+kRight)/dx**2/2 
                A[n,nRight] = kRight/dx**2/2
                A[n,nLeft] = kLeft/dx**2/2
                b[n] = 0


            #top right                
            if (i==ndx-1 and j==0):

                A[n,n] = -kLeft/dx**2/2 
                A[n,nLeft] = kLeft/dx**2/2

                A[n,n] += -he/dx/2
                b[n] = -he*Te/dx/2

            if (i==ndx-1 and j==ndy-1):

                A[n,n] = -kLeft/dx**2/2 
                A[n,nLeft] = kLeft/dx**2/2

                A[n,n] += -he/dx/2
                b[n] = -he*Te/dx/2
    


            if isMetalNode(i,j,MS_ids):    
               
                if MSID == 0:
                    A[n,n] += -1*kMetal*eMetal/dx**3
                    A[n,nMS_next] += kMetal*eMetal/dx**3
                    
                elif MSID == nMSNodes -1:
    
                    A[n,n] += -1*kMetal*eMetal/dx**3
                    A[n,nMS_prev] += kMetal*eMetal/dx**3
                
                else:
                    A[n,nMS_prev] += kMetal*eMetal/dx**3
                    A[n,nMS_next] += kMetal*eMetal/dx**3
                    A[n,n] += -2*kMetal*eMetal/dx**3
    
            
    T = np.linalg.solve(A, b)

    heatFlux = -entreAxe*hi*(np.mean(T[range(ndy)])-Ti) # i = 0 
    # should be equal to entreAxe*he*(np.mean(T[range(npoints-ndy,npoints)])-Te)
        
    
    metalProps = {'kMetal':kMetal,'eMetal':eMetal,'entreAxe':entreAxe}   
    boundaryConditions={'Ti':Ti,'Te':Te,'hi':hi,'he':he}
    RvaluesDict = computeUandRValues(heatFlux,metalProps,boundaryConditions,ndy,T,npoints,eIsol,kIsol,Xuns,Yuns)

    if (plot):
       annotatedPlot(RvaluesDict,metalProps,boundaryConditions,ndy,T,npoints,eIsol,kIsol,Xuns,Yuns,xMetal,yMetal)
 
    
    return [Xuns,Yuns,T]
    

def computeUandRValues(heatFlux,metalProps,boundaryConditions,ndy,T,npoints,eIsol,kIsol,Xuns,Yuns):
    
    
    Rsi = 1/boundaryConditions['hi']
    Rse = 1/boundaryConditions['he']
    

    Uglobal = heatFlux/metalProps['entreAxe']/(boundaryConditions['Ti']-boundaryConditions['Te'])
    Rglobal = 1/Uglobal
    
    RLayer = Rglobal - Rsi - Rse
    ULayer = 1/RLayer
    
    Rtheoritical = np.sum(np.array(eIsol)/np.array(kIsol))
    
    print('Unperturbed R-value ',np.round(Rtheoritical,2),'W/m²K')
    print('R value ',np.round(RLayer,2),'m²K/W')   
    print('U value ',np.round(ULayer,2),'W/m²K')   
    
    return {'Rtheoritical':Rtheoritical,
            'RLayer':RLayer,
            'Rglobal':Rglobal
            }

    
def annotatedPlot(RvaluesDict,metalProps,boundaryConditions,ndy,T,npoints,eIsol,kIsol,Xuns,Yuns,xMetal,yMetal):

    plt.figure(figsize=(18,6))
    
    plotMetalNodes(xMetal,yMetal)

    
    Rsi = 1/boundaryConditions['hi']
    Rse = 1/boundaryConditions['he']
    
    eCum=0
    for e in eIsol:
        eCum += e
        plt.axhline(eCum,color='k',lw=1.0)
        
    plt.axis('equal')
   
        
    plt.annotate('Re = '+str(np.round(Rse,2)),(metalProps['entreAxe']-0.01,eCum+0.01),xycoords='data',horizontalalignment='right')
    plt.annotate('Ri = '+str(np.round(Rsi,2)),(metalProps['entreAxe']-0.01,-0.01),xycoords='data',verticalalignment='top',horizontalalignment='right')


    annotation = 'Layer unpertubed R value: '+str(np.round(RvaluesDict['Rtheoritical'],2))+' m²K/W\n'
    annotation+= 'Layer calculated R value: '+str(np.round(RvaluesDict['RLayer'],2))+' m²K/W\n'
    annotation+= 'Layer calculated R value (with RSI + RSE): '+str(np.round(RvaluesDict['Rglobal'],2))+' m²K/W'

    plt.annotate(annotation,(0.01,0.8),xycoords='axes fraction',horizontalalignment='left')
    
    hypotheses = ''
    hypotheses +='k$_{metal}$ = '+str(metalProps['kMetal'])+' W/mK\n'
    hypotheses +='Profile thickness = '+str(metalProps['eMetal']*1000)+' mm\n'
    
    plt.annotate(hypotheses,(0.01,-0.01),xycoords='data',horizontalalignment='left',verticalalignment='top')

    eCum=0
    for e,k in zip(eIsol,kIsol):
        
        eCum += e
        
        plt.annotate('e = '+str(e*100)+' cm, k = '+str(k),(0.01,eCum-2e-3),xycoords='data',horizontalalignment='left',verticalalignment='top')
        

    c=plt.tricontourf(Yuns, Xuns, T,100,cmap='plasma')
   
    #show in cm instead of m    
    xti,xlb = plt.xticks()
    plt.xticks(xti,[str(int(100*l)) for l in xti])

    
    yti,ylb = plt.yticks()
    plt.yticks(yti,[str(int(100*l)) for l in yti])
   
    
    plt.axis('equal')
    plt.colorbar(ticks=np.linspace(boundaryConditions['Te'],boundaryConditions['Ti'],11,endpoint=True))

    
             

def mapMetalNodes(layer_ndx,layer_ndy,dx,shape,wMetal,hMetal,pMetal):

  
    if (shape=='C-shape'):
        ids,nNodes,xMS,yMS = mapCShapeNodes(layer_ndx,layer_ndy,dx,wMetal,hMetal,pMetal)
            
    elif (shape=='U-shape'):
        ids,nNodes,xMS,yMS = mapUShapeNodes(layer_ndx,layer_ndy,dx,wMetal,hMetal,pMetal)

       
    return ids,nNodes,xMS,yMS

def plotMetalNodes(xMS,yMS):
    
    plt.plot(yMS,xMS,'-',color='k',lw=2.0)



def mapCShapeNodes(layer_ndx,layer_ndy,dx,wMetal,hMetal,pMetal):

    #Lets call it C-shape
    
    #This configuration
    #
    #    ******
    #         *
    #         *          ^
    #         *          |
    #         *          |
    #         *          |
    #         *          |
    #         *          |
    #    ******     HEAT TRANSFER
    #
    
    iStart = int((pMetal+hMetal)/dx)
    jStart = int(layer_ndy/2)  # on commence à peu près à la moitié
    
    n_vertical_nodes = int(wMetal/dx) -1
    n_horizontal_nodes = int(hMetal/dx)+1
    
    
    nNodes = n_vertical_nodes + 2*n_horizontal_nodes
    
    
    ids = np.zeros((layer_ndx,layer_ndy))-1.
    
    xMS = []
    yMS = []
    
    for n in range(nNodes):
        
        if (n<n_horizontal_nodes):
        
            i = iStart - n
            j = jStart
            
            
        elif (n<=n_vertical_nodes+n_horizontal_nodes):
            
            print(n)
            
            j = jStart + (n - n_horizontal_nodes) + 1
            i = iStart  - n_horizontal_nodes + 1
            
        else:
            
            j = jStart + n_vertical_nodes + 1
            i = iStart - n_horizontal_nodes + 1 + (n - n_vertical_nodes - n_horizontal_nodes)
            
            
        ids[i,j] = n

        xMS.append(i*dx)
        yMS.append(j*dx)


    return ids,nNodes,xMS,yMS


def mapUShapeNodes(layer_ndx,layer_ndy,dx,wMetal,hMetal,pMetal):

    #Lets call it U-shape
    
    #This configuration
    #                    ^
    #   *      *         |
    #   *      *         |
    #   *      *         |
    #   ********         |
    #                HEAT TRANSFER
    #
    
    iStart = int((pMetal)/dx)

    MS_ndx = int(wMetal/dx)+1

    
    jStart = int(layer_ndy/2)
    #iStart = 0
    
    n_vertical_nodes = int(hMetal/dx) +1
    n_horizontal_nodes = MS_ndx-2
    
    nNodes = 2*n_vertical_nodes + n_horizontal_nodes
    
    ids = np.zeros((layer_ndx,layer_ndy))-1.
    
    xMS = []
    yMS = []
    
    for n in range(nNodes):
        
        if (n<n_vertical_nodes):
        
            i = iStart
            j = jStart + n
            
            
        elif (n<=n_vertical_nodes+n_horizontal_nodes):
            
            i = iStart + (n-n_vertical_nodes) + 1
            j = jStart + n_vertical_nodes -1
            
        else:
            
            i = iStart + n_horizontal_nodes + 1
            j = jStart + (n_vertical_nodes) - 1 - (n - n_vertical_nodes - n_horizontal_nodes)
            
            
        ids[i,j] = n

        xMS.append(i*dx)
        yMS.append(j*dx)
       
    return ids,nNodes,xMS,yMS



def getGlobalNodeNumber(i,j,ndy):
    
    return i*ndy + j
            

  
 
    
def computeNodesLeftAndRightConductivity(eIsol,kIsol,dx,ndx):
    
    #For each node layer i, retruns the conductivity of the left cell and the right cell
    
    kI=np.zeros((ndx,2))+kIsol[0] #col 0: left value, col1: right value
    
    eCumulated=0
    previousPivot = 0

    for e,k in zip(eIsol,kIsol):

        eCumulated+=e
        
        iPivot = int(eCumulated/dx) #fin de la couche courante              
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


    
if __name__ == '__main__' :
    main()
    
    
    
    
    
X,Y,T = multiLayer_hConv_MS(eIsol=[0.01,0.01,0.05,0.01],
                            kIsol=[0.20,0.13,0.035,0.13], 
                            pMetal=0.02, 
                            wMetal = 0.05, 
                            hMetal=0.03, 
                            dx=0.005, 
                            MStype='U-shape',
                            plot=False)
X=X*100
Y=Y*100
    
    
    
