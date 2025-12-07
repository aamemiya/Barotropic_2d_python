import os 
from types import MethodType
import numpy as np, math
import h5netcdf
from fluidsim.solvers.ns2d.solver import Simul
from fluidsim.base.output.base import SpecificOutput
import common

nx=128
dt0=0.004
dt_out=0.4
intv_out=int(round(dt_out/dt0))
length=100.0

# Keep a reference to the original method
_orig_has_to_online_save = SpecificOutput._has_to_online_save

# Install the patch globally
SpecificOutput._has_to_online_save = common._has_to_online_save_every_n_steps

params = Simul.create_default_params()
params.oper.nx = params.oper.ny = nx
params.oper.Lx = params.oper.Ly = 2.0 * 3.141592653589793
params.time_stepping.t_end = length
params.time_stepping.deltat0 = dt0
params.time_stepping.USE_CFL = False

params.forcing.enable = True
params.forcing.type = "tcrandom"      # e.g. time-correlated random ring forcing
params.forcing.nkmin_forcing = 4
params.forcing.nkmax_forcing = 5
params.forcing.normalized.constant_rate_of = "energy"
params.forcing.forcing_rate = 0.2        # set target energy input rate
params.nu_4 = 4.0e-6                   # hyperviscosity (example)
params.nu_m4 = 5e-2                   # hypoviscosity (example)

params.output.sub_directory=os.path.join(os.getcwd(),"output")
params.output.periods_save.phys_fields = dt_out
params.output.periods_print["print_stdout"]=10*dt_out

params.init_fields.type="noise"
params.init_fields.noise.length=0.0
sim = Simul(params)
op = sim.oper

# --- open a NetCDF file to log the forcing ---
path_nc = sim.output.path_run + "/forcing.nc"
nc = h5netcdf.File(path_nc, "w")
nc.dimensions = {
    "time": 0,
    "y": op.ny,
    "x": op.nx,
    "l": op.ny,
    "k": op.nx // 2 + 1,
}
vtime = nc.create_variable("time", ("time",), dtype="f8")
vrot = nc.create_variable("rot_forcing", ("time", "y", "x"), dtype="f4")
vrot_fft_r = nc.create_variable("rot_fft_forcing_r", ("time", "l", "k"), dtype="f4")
vrot_fft_i = nc.create_variable("rot_fft_forcing_i", ("time", "l", "k"), dtype="f4")

_it = 0
it_forcing=0
time_intv_forcing=20

digits=abs(math.floor(np.log10(dt0)))

# --- wrap the time-stepping function ---
orig_step = sim.time_stepping.one_time_step_computation

# --- define the callback executed every time step ---
def one_step_and_save():
    global _it
    global it_forcing
    global time_intv_forcing
    orig_step()  # perform the normal time step
    Fh = sim.forcing.get_forcing()   # spectral forcing (complex array)
    Fp = op.ifft(Fh)             # physical forcing (complex array)

    if np.mod(_it,time_intv_forcing) == 0: 
        nc.resize_dimension("time", it_forcing + 1)
        vtime[it_forcing] = round(sim.time_stepping.t,digits)
        vrot[it_forcing, :, :] = Fp.real.astype("f4")
        vrot_fft_r[it_forcing, :, :] = Fh.real.astype("f4")
        vrot_fft_i[it_forcing, :, :] = Fh.imag.astype("f4")
        nc.flush()
        it_forcing += 1

    _it += 1

# replace the integrator's single-step method
sim.time_stepping.one_time_step_computation = one_step_and_save

sim.time_stepping.start()
nc.close()
