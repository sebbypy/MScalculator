# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
import io
import base64

def main():

    plt.close('all')
    
    multiLayer_hConv_MS(dx=0.01)
   
   
    

def multiLayer_hConv_MS(*,eIsol = [0.01,0.02,0.1] , kIsol=[0.20,0.13,0.035], pMetal=0.03, wMetal = 0.05, hMetal = 0.05, entreAxe = 0.6,dx = 5e-3 ,kMetal = 50, eMetal=6e-4, hconv=10):

    #eIsol: list of layers thickness
    #kIsol: list of layers lambda
    #pMetal = postiion of the metal from inside (cm)
        
    dy = dx        
    
    Te=0
    Ti=1
    
    
    ndx = int(np.sum(eIsol)/dx)+1
    ndy= int(entreAxe/dy)+1
    npoints = ndx*ndy


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
    

    ndxMS = int(wMetal/dx)+1
    istartMS = int(pMetal/dx)

    MS_ids,nMSNodes = compute_MS_ids(ndx,ndy,dx,ndxMS,hMetal,iStart=istartMS) # table that contains -1 if nothing special or a null or positive id  if MS

    A = np.zeros((npoints,npoints))
    b = np.zeros(npoints)
    T=np.zeros(npoints)
    
    
    Xuns=np.zeros(npoints)
    Yuns=np.zeros(npoints)
    
    
    for i in range(ndx):
        for j in range(ndy):

            
            MSID = MS_ids[i,j] #ID of METAL STUD ELEMENTS
            nMS_prev = -1
            nMS_next = -1
            
            if (MSID>=0):
                #print(MSID)
                
                try:
                    iprev,jprev= getMSNodeFromID(MS_ids,MSID-1)
                    nMS_prev = iprev*ndy + jprev
                except:
                    nMS_prev = -1
                    
                try:                
                    inext,jnext= getMSNodeFromID(MS_ids,MSID+1)
                    nMS_next = inext*ndy + jnext
                except:
                    nMS_next = -1
                
            
            n = i*ndy + j

            Xuns[n] = i*dx
            Yuns[n] = j*dy
            
            ni_minus_1 = (i-1)*ndy + j
            ni_plus_1  = (i+1)*ndy + j
            
            nj_minus_1 = i*ndy + (j-1)
            nj_plus_1  = i*ndy + (j+1)


            kLeft  = kI[i,0]
            kRight = kI[i,1]
            

            #case 1 : normal cell
            if (i>0 and j>0 and i<ndx-1 and j<ndy-1):
                               
                A[n,n] = -(kLeft+kRight)/dx**2 - (kLeft+kRight)/dy**2
                A[n,ni_minus_1] = kLeft/dx**2
                A[n,ni_plus_1] = kRight/dx**2
                A[n,nj_minus_1] = (kLeft+kRight)/2/dy**2
                A[n,nj_plus_1] = (kLeft+kRight)/2/dy**2
                b[n] = 0
            
            #case 2: normal left BC
            if (i==0 and (j !=0 and j != ndy-1)):
               
                A[n,n] = -kRight/dx**2 - 2*kRight/dy**2/2
                A[n,ni_plus_1] = kRight/dx**2
 
                A[n,nj_minus_1] = kRight/dy**2/2
                A[n,nj_plus_1] = kRight/dy**2/2

                A[n,n] += -hconv/dx #convective
                b[n] = -hconv*Ti/dx

            #botm left 
            if (i==0 and j==0):

                A[n,n] = -kRight/dx**2/2 #- 2/dy**2/2
                A[n,ni_plus_1] = kRight/dx**2/2
                
                A[n,n] += -hconv/dx/2
                b[n] = -hconv*Ti/dx/2

            #top left                
            if (i==0 and j==ndy-1):

                A[n,n] = -kRight/dx**2/2 
                A[n,ni_plus_1] = kRight/dx**2/2

                A[n,n] += -hconv/dx/2
                b[n] = -hconv*Ti/dx/2

            #case 2: normal right
            if (i== ndx-1 and (j !=0 and j != ndy-1)):
                
                A[n,n] = -kLeft/dx**2 - 2*kLeft/dy**2/2
                A[n,ni_minus_1] = kLeft/dx**2
                A[n,nj_minus_1] = kLeft/dy**2/2
                A[n,nj_plus_1] = kLeft/dy**2/2

                A[n,n] += -hconv/dx #convective
                b[n] = -hconv*Te/dx

            
            #case 4: normal top: symmetric
            if (j== 0 and (i !=0 and i != ndx-1)):
                
                A[n,n] = -(kLeft+kRight)/dx**2/2 
                A[n,ni_plus_1] = kRight/dx**2/2
                A[n,ni_minus_1] = kLeft/dx**2/2
                b[n] = 0
                
            #case 5: normal bot: symmetric
            if (j== ndy-1 and (i !=0 and i != ndx-1)):
                
                A[n,n] = -(kLeft+kRight)/dx**2/2 
                A[n,ni_plus_1] = kRight/dx**2/2
                A[n,ni_minus_1] = kLeft/dx**2/2
                b[n] = 0


            #top right                
            if (i==ndx-1 and j==0):

                A[n,n] = -kLeft/dx**2/2 
                A[n,ni_minus_1] = kLeft/dx**2/2

                A[n,n] += -hconv/dx/2
                b[n] = -hconv*Te/dx/2

            if (i==ndx-1 and j==ndy-1):

                A[n,n] = -kLeft/dx**2/2 
                A[n,ni_minus_1] = kLeft/dx**2/2

                A[n,n] += -hconv/dx/2
                b[n] = -hconv*Te/dx/2
    
    

            if MSID > 0 and MSID < nMSNodes-1: 
                #print('This is a MS INTERNAL NODE')
                A[n,nMS_prev] += kMetal*eMetal/dx**3
                A[n,nMS_next] += kMetal*eMetal/dx**3
                
                A[n,n] += -2*kMetal*eMetal/dx**3
                
            if MSID == 0:
                A[n,n] += -1*kMetal*eMetal/dx**3
                A[n,nMS_next] += kMetal*eMetal/dx**3
                
            if MSID == nMSNodes -1:

                A[n,n] += -1*kMetal*eMetal/dx**3
                A[n,nMS_prev] += kMetal*eMetal/dx**3
                
            
    T = np.linalg.solve(A, b)
    
    PhiInt = entreAxe*hconv*(np.mean(T[range(ndy)])-Ti) # i = 0 
    PhiExt = entreAxe*hconv*(np.mean(T[range(npoints-ndy,npoints)])-Te)

    print(PhiInt,PhiExt)

    Rsi = 1/hconv
    Rse = 1/hconv
    

    Uglobal = PhiExt/entreAxe/(Ti-Te)
    Rglobal = 1/Uglobal
    
    RLayer = Rglobal - Rsi - Rse
    ULayer = 1/RLayer
    
    
    #print(PhiInt,PhiExt)
    print('Unperturbed R-value ',np.round(np.sum(np.array(eIsol)/np.array(kIsol)),2),'W/m²K')
    print('R value ',np.round(RLayer,2),'m²K/W')   
    print('U value ',np.round(ULayer,2),'W/m²K')   
    
    #print(max(T))
    #print(min(T))
    
    #c=plt.tricontourf(Xuns, Yuns, T,100,cmap='plasma')
    c=plt.tricontourf(Yuns, Xuns, T,100,cmap='plasma')
    
    eCum=0
    for e in eIsol:
        eCum += e
        plt.axhline(eCum,color='k',lw=1.0)
    
    plt.axis('equal')
   
    
    
    plt.annotate('Re = '+str(np.round(1/hconv,2)),(entreAxe-0.01,eCum+0.01),xycoords='data',horizontalalignment='right')
    plt.annotate('Ri = '+str(np.round(1/hconv,2)),(entreAxe-0.01,-0.01),xycoords='data',verticalalignment='top',horizontalalignment='right')


    annotation = 'Layer unpertubed R value: '+str(np.round(np.sum(np.array(eIsol)/np.array(kIsol)),2))+' m²K/W\n'
    annotation+= 'Layer calculated R value: '+str(np.round(RLayer,2))+' m²K/W'
    plt.annotate(annotation,(0.01,0.8),xycoords='axes fraction',horizontalalignment='left')
    
    
    hypotheses = ''
    #hypotheses +='k$_{insulation}$ = '+str(kIsol)+' W/mK\n'
    #hypotheses +='e$_{insulation}$ = '+str(eIsol*1e3)+' mm\n'
    hypotheses +='k$_{metal}$ = '+str(kMetal)+' W/mK\n'
    hypotheses +='Profile thickness = '+str(eMetal*1000)+' mm\n'
    
    plt.annotate(hypotheses,(0.01,-0.01),xycoords='data',horizontalalignment='left',verticalalignment='top')

    eCum=0
    for e,k in zip(eIsol,kIsol):
        
        eCum += e
        
        plt.annotate('e = '+str(e*100)+' cm, k = '+str(k),(0.01,eCum-2e-3),xycoords='data',horizontalalignment='left',verticalalignment='top')
        


    
    #show in cm instead of m    
    xti,xlb = plt.xticks()
    plt.xticks(xti,[str(int(100*l)) for l in xti])

    
    yti,ylb = plt.yticks()
    plt.yticks(yti,[str(int(100*l)) for l in yti])
    
    plt.axis('equal')
    plt.colorbar(ticks=np.linspace(Te,Ti,11,endpoint=True))
    plt.clim(Te,Ti)         


def compute_MS_ids(layer_ndx,layer_ndy,dx,MS_ndx,MS_height,iStart=0):
    
    
    jStart = int(layer_ndy/2)
    #iStart = 0
    
    n_vertical_nodes = int(MS_height/dx) +1
    n_horizontal_nodes = MS_ndx-2
    
    nNodes = 2*n_vertical_nodes + n_horizontal_nodes
    
    ids = np.zeros((layer_ndx,layer_ndy))-1.
    print(np.shape(ids))
    
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


    plt.figure(figsize=(16,6))        
    plt.plot(yMS,xMS,'-',color='k',lw=2.0)
       
    return ids,nNodes
            

def getMSNodeFromID(IDMatrix,searchedMSID):
   
    i,j = np.where(IDMatrix == searchedMSID)
    
    return i[0],j[0]
    

    
 
 
main()


buf = io.BytesIO()
plt.savefig(buf, format='png')
buf.seek(0)
img_str = 'data:image/png;base64,' + base64.b64encode(buf.read()).decode('UTF-8')
