import os 
import numpy as np
from fluidsim.solvers.ns2d.solver import Simul
from fluidsim.base.output.base import SpecificOutput
import matplotlib

def _has_to_online_save_every_n_steps(self):
    """Return True every N iterations instead of using time buckets.

    N is computed once as round(period_save / dt), assuming (nearly) constant dt.
    """
    # If saving is disabled for this output, never save
    if self.period_save == 0:
        return False

    sim = self.sim
    it = sim.time_stepping.it

    # Lazy initialization the first time this is called for a given SpecificOutput
    if not hasattr(self, "_n_save_steps"):
        dt = sim.time_stepping.deltat

        if dt <= 0.0:
            # Fallback: save every step if something odd happens
            self._n_save_steps = 1
        else:
            # N ≈ period_save / dt, rounded to nearest integer, at least 1
            self._n_save_steps = max(1, int(round(self.period_save / dt)))

        # Consider that we last saved at the current iteration
        # (init files / first save has already happened)
        self._it_last_save = it

    # Standard "every N steps" logic
    if it - self._it_last_save >= self._n_save_steps:
        self._it_last_save = it
        # Keep t_last_save consistent for end_of_simul and other code
        self.t_last_save = sim.time_stepping.t
        return True

    return False


vor_colors = [
    "#000066", 
    "#0000cc", 
    "#0000ff", 
    "#0066ff",  
    "#3399ff",  
    "#66ccff",  

    "#ffffff", 
    "#ffffff", 

    "#ffff99", 
    "#ffcc66", 
    "#ff9933", 
    "#ff3300",  
    "#ff0000",  
    "#800000",  
]
vor_colormap = matplotlib.colors.ListedColormap(vor_colors[1:-1])
vor_colormap.set_over(vor_colors[-1])
vor_colormap.set_under(vor_colors[0])

vor_levels = np.arange(-12,14,2)
vor_norm=matplotlib.colors.BoundaryNorm(vor_levels, len(vor_levels))


