"""
This is the main progam code that sets up the topology optimisation problem.
This optimisation tries to minimize the stress intensity factor. Which should
maximise the fatigue crack propegation life and thus the increase damage
tolerance.

Bram Lagerweij
Aerospace Structures and Materials Department TU Delft
2018
"""

import time
import math
import numpy as np

from loads import EdgeCrack, DoubleEdgeCrack, CompactTension
from constraints import DensityConstraint
from fesolvers import CvxFEA, SciPyFEA, CGFEA
from topopt import Topopt
from plotting import Plot


if __name__ == "__main__":
    # material properties
    young = 1
    poisson = 0.3
    ext_stiff = 0.0
    
    # constraints
    Emin = 1e-9
    volfrac = 1.1
    move = 0.25
    
    # mesh dimensions
    nelx = 500
#    nely = 100
    crack_length = 250
    
    # optimization parameters
    penal = 1
    rmin = 1.5
    filt = 'density'
    loopy = 5000  # math.inf
    delta = 0.001

    # plotting and printing options
    directory = 'CT0053/'
    verbose = True
    plotting = True
    save_plot = True
    history = True
    save_pointcloud = False
    save_array = True

    # loading case object, other classes can be selected and created
    load = CompactTension(nelx, crack_length, young, Emin, poisson, ext_stiff)

    # constraints object created
    den_con = DensityConstraint(load, move, volume_frac=volfrac, density_min=1, density_max=2)

    # FEA object is generated, other solvers can be selected and created
    fesolver = CvxFEA(verbose=verbose)

    # create optimizer object and initialise the problem
    optimizer = Topopt(den_con, load, fesolver, verbose=verbose, history=history)

    # compute
    t = time.time()
    x, x_history, ki = optimizer.layout(penal, rmin, delta, loopy, filt)
    print('Elapsed time is: ', time.time() - t, 'seconds.')

    # plotting
    pl = Plot(load, directory)
    pl.loading(load)
    pl.boundary(load)

    if history:
        for i in x_history:
            pl.add(i, animated=True)
        pl.save('video')

    pl.add(x, animated=False)

    if save_plot:
        pl.save('figure')

    if plotting:
        pl.show()

    if save_pointcloud:
        xm = np.vstack((x, np.flip(x, 0)))
        pl.saveXYZ(xm, x_size=60, thickness=1)

    if save_array:
        from numpy import save
        save(directory+'x', x)
