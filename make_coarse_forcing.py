import os 
import numpy as np
import h5netcdf

# --- open a NetCDF file to load the forcing ---
path_nc_in = os.path.join(os.getcwd(),"forcings","forcing_x2.nc")
nc_in = h5netcdf.File(path_nc_in, "r")

vrot_in=nc_in["rot_forcing"][:]
forcing_rot_r_in=nc_in["rot_fft_forcing_r"][:]
forcing_rot_i_in=nc_in["rot_fft_forcing_i"][:]
vtime_in=nc_in["time"][:]
nx=nc_in.dimensions['x'].size
ny=nc_in.dimensions['y'].size
nt=nc_in.dimensions['time'].size
# --- open a NetCDF file to log the forcing ---
path_nc_out = os.path.join(os.getcwd(),"forcings","forcing_x4.nc")
nc_out = h5netcdf.File(path_nc_out, "w")
nc_out.dimensions = {
    "time": 0,
    "y": ny//2,
    "x": nx//2,
    "l": ny//2,
    "k": nx//4 + 1,
}
vtime = nc_out.create_variable("time", ("time",), dtype="f8")
vrot_out = nc_out.create_variable("rot_forcing", ("time", "y", "x"), dtype="f4")
forcing_rot_r_out = nc_out.create_variable("rot_fft_forcing_r", ("time", "l", "k"), dtype="f4")
forcing_rot_i_out = nc_out.create_variable("rot_fft_forcing_i", ("time", "l", "k"), dtype="f4")

def reduce(array_in):
    top = array_in[ : ny//4, : nx//4 + 1]
    bottom = array_in[ ny-ny//4:, : nx//4 + 1]
    return np.vstack([top,bottom])

for it in range(nt):
    nc_out.resize_dimension("time", it + 1)
    if np.mod(it,100) == 0 :
        print(it)
    vtime[it]=vtime_in[it]
    vrot_out[it,:,:]=vrot_in[it,::2,::2]
    forcing_rot_r_out[it,:,:]=reduce(forcing_rot_r_in[it,:,:])
    forcing_rot_i_out[it,:,:]=reduce(forcing_rot_i_in[it,:,:])

nc_in.close()   
nc_out.close()   
