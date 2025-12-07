import os
import sys
import glob

import numpy as np
import netCDF4
import matplotlib
import matplotlib.pyplot as plt
from common import vor_norm, vor_levels, vor_colormap

indir=sys.argv[1]
files=sorted(glob.glob(indir + "/state_phys*.nc"))

ista,iend,intv = 0,-1,1
if len(sys.argv) >= 3 :
    cslice=sys.argv[2]
    csta,cend,cntv=cslice.split(":")
    if csta: ista=int(csta)
    if cend: iend=int(cend) 
    if cntv: intv=int(cntv) 

it = 0
for f in files[ista:iend:intv] : 
    nc = netCDF4.Dataset(f,'r')
    vor = np.array(nc.groups['state_phys'].variables['rot'][:])
    nx = np.array(nc.groups['state_phys'].dimensions['x'].size)
    ny = np.array(nc.groups['state_phys'].dimensions['y'].size)
    nc.close

    x1=np.linspace(1,nx,num=nx)
    y1=np.linspace(1,ny,num=ny)
    x,y=np.meshgrid(x1,y1)


    cs=plt.pcolormesh(x,y,vor, norm=vor_norm,cmap=vor_colormap)
#    cs=plt.contourf(x,y,vor,levels=vor_levels,norm=vor_norm, cmap=vor_colormap,extend="both")
    cbar = plt.colorbar(cs,location='right')
    fname="vor_"+str(it).zfill(4)+".png"
    print(fname)
    plt.savefig(fname)
    plt.clf()
    it += 1

