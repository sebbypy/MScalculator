import matplotlib.pyplot as plt
import numpy as np



def annotatedPlot(solver,grid=False,annotate=True,contour=True,saveFig=True,figureName='figure.pdf'):

    fig, (ax1, ax2) = plt.subplots(1, 2,figsize=(10,6))
       
    ax2.axis('off')
    
    Rsi = 1/solver.hi
    Rse = 1/solver.he
    
    eCum=0
    for e in solver.layersThickness:
        eCum += e
        ax1.axvline(eCum,color='k',lw=1.0)

    plotMetalProfile({'shape':solver.MStype,
                      'pMetal':solver.pMetal,
                      'eMetal':solver.eMetal,
                      'hMetal':solver.hMetal,
                      'entreAxe':solver.entreAxe,
                      'wMetal':solver.wMetal},ax=ax1)
        
    ax1.axis('equal')
   
    if (annotate):        
        ax2.annotate('Re = '+str(np.round(Rse,2)),(0.01,0.95),xycoords='data')
        ax2.annotate('Ri = '+str(np.round(Rsi,2)),(0.01, 0.90),xycoords='data')
    

        eCum=0      
        nLines = 0
        
        for e,k in zip(solver.layersThickness,solver.layersConductivity):
            eCum += e           
            if not np.isnan(k):
                plt.annotate('e = '+str(e*100)+' cm, k = '+str(k),(0.01,0.85-0.05*nLines),xycoords='axes fraction',horizontalalignment='left')
            else:
                plt.annotate('e = '+str(e*100)+' cm, R = '+str(solver.ResistanceAirLayer)+' (Air layer)',(0.01,0.85-0.05*nLines),xycoords='axes fraction',horizontalalignment='left')
            nLines+=1
            

        hypotheses = ''
        hypotheses +='k$_{metal}$ = '+str(solver.kMetal)+' W/mK\n'
        hypotheses +='Profile thickness = '+str(solver.eMetal*1000)+' mm\n'
        
        plt.annotate(hypotheses,(0.01,0.5),xycoords='axes fraction',horizontalalignment='left')



        #annotation = 'Theoritical R without thermal bridge (without convection): '+str(np.round(RvaluesDict['R1'],2))+' m²K/W\n'

        RvaluesDict = solver.computeUandRValues()
        
        annotation = 'Theoritical R without thermal bridge: '+str(np.round(RvaluesDict['R1'],2))+' m²K/W\n'
        annotation+= 'Calculated R with thermal bridge: '+str(np.round(RvaluesDict['R3'],2))+' m²K/W'
    
        plt.annotate(annotation,(0.01,0.40),xycoords='axes fraction',horizontalalignment='left')


    Xuns,Yuns = solver.getFlattenedXandY()
    T = solver.T

    if(grid):
        ax1.plot(Xuns,Yuns,'ko',markersize=1)


    if (contour):
        c=ax1.tricontourf(Xuns, Yuns, T,11,cmap='coolwarm')
        
        clines=ax1.tricontour(Xuns, Yuns, T,11,colors='black',linewidths=0.5)
        
        fig.colorbar(c,ticks=np.linspace(solver.Te,solver.Ti,11,endpoint=True),ax=ax1)
   
    yti = ax1.get_yticks()
    ax1.set_yticklabels([str(int(round(100*l))) for l in yti])



    xti = list(np.cumsum(solver.layersThickness))

    ax1.set_xticks(xti)
    ax1.set_xticklabels([str(int(round(100*l))) for l in xti])
    

    if saveFig:
        

        plt.savefig(figureName)





def plotMetalProfile(metalData,ax):

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
                
    
    ax.plot(x,y,ls='-',color=color,lw=3.0)

    return  x,y
