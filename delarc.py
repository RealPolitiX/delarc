# -*- coding: utf-8 -*-
"""
@author: R. Patrick Xian
"""

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.figure import figaspect
from matplotlib.font_manager import FontProperties
import scipy.io as sio


def sliceview3d(datamat, axis=0, numbered=True, **kwds):
    
    # Gather parameters from input
    cutdim = datamat.shape[axis]
    nc = kwds.pop('ncol', 4)
    nr = kwds.pop('nrow', np.ceil(cutdim/nc).astype('int'))
    cmap = kwds.pop('cmp', 'Greys')
    cscale = kwds.pop('cscale', 'log')
    numcolor = kwds.pop('numcolor', 'black')
    ngrid = nr*nc
    
    # Construct a grid of subplots
    fw, fh = 5*figaspect(np.zeros((nr, nc)))
    f, ax = plt.subplots(nrows=nr, ncols=nc, figsize=(fw,fh))
    
    # Put each figure in a subplot, remove empty subplots
    for i in range(ngrid):
        
        # Select the current axis based on the index
        axcurr = ax[np.unravel_index(i, (nr, nc))]
        
        if i <= cutdim - 1:
            # Roll the slicing axis to the start of the matrix before slicing
            img = np.rollaxis(datamat, axis)[i,:,:]
            im = axcurr.imshow(img, cmap=cmap)
            
            # Set color scaling for each image individually
            if cscale == 'log':
                im.set_norm(mpl.colors.LogNorm())
            elif cscale == 'linear':
                im.set_norm(mpl.colors.Normalize())
            
            axcurr.get_xaxis().set_visible(False)
            axcurr.get_yaxis().set_visible(False)
            
            if numbered == True:
                axcurr.text(0.03, 0.92, '#%s' % i, fontsize=15, color=numcolor, transform=axcurr.transAxes)
        else:
            f.delaxes(axcurr)
    
    # Add the main title
    figtitle = kwds.pop('maintitle', '')
    if figtitle:
        f.text(0.5, 0.955, figtitle, horizontalalignment='center', fontproperties=FontProperties(size=20))
    
    wsp = kwds.pop('wspace', 0.05)
    hsp = kwds.pop('hspace', 0.05)
    plt.subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.95, wspace=wsp, hspace=hsp)
    
    return ax.ravel()


def removeitems(flist, rmlist, matname, savefile=False, **kwargs):
    # Remove corrupted images from an image cube
    
    # Retrieve input parameters
    if savefile == True:
        savedir = kwargs.pop('savedir', '')
        savetext = kwargs.pop('savetext', '')
        dpi = kwargs.pop('dpi', 300)
    
    titletext = kwargs.pop('titletext', '')
    cubeslice = kwargs.pop('cubeslice', np.s_[:,:,:])
    for k, v in list(rmlist.items()):
        
        # Pick out and load datacube from each suspect file (suspf)
        suspf = flist[int(k)]
        fname = suspf.split('\\')[-1]
        tp = fname.split('fs')[0]
        datadict = sio.loadmat(suspf)
        datacube = datadict[matname]
        
        # Delete the corrupted individual images to save to edited datacube
        rdatacube = np.delete(datacube, v, axis=2)
        
        # Restore the cleaned image matrix to origin file
        datadict[matname] = rdatacube
        sliceview3d(rdatacube[cubeslice], maintitle=titletext + 'img#%s, ' % k + tp + ' fs', **kwargs)
        
        # save files
        if savefile == True:
            plt.savefig(savedir + savetext + tp + 'fs.png', dpi=dpi, bbox_inches='tight')
            sio.savemat(savedir + '\\' + fname, datadict)