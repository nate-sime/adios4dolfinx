from adios4dolfinx import write_mesh_perm, write_function, read_mesh, read_function_perm
import dolfinx
from mpi4py import MPI
import pathlib
import time
import pytest
import ufl
import numpy as np


@pytest.mark.parametrize("encoder, suffix", [("BP4", ".bp")])  # , ("HDF5", ".h5"), ("BP5", ".bp")])
@pytest.mark.parametrize("ghost_mode", [dolfinx.mesh.GhostMode.shared_facet])
def test_mesh_read_writer(encoder, suffix, ghost_mode):

    N = 2
    file = pathlib.Path(f"output/adios_mesh_{encoder}")
    if MPI.COMM_WORLD.rank == 0:
        mesh_loc = dolfinx.mesh.create_unit_square(MPI.COMM_SELF, N, N, ghost_mode=ghost_mode)
        write_mesh_perm(mesh_loc, file.with_suffix(suffix), encoder)
        V = dolfinx.fem.FunctionSpace(mesh_loc, ("N1curl", 1))
        u = dolfinx.fem.Function(V)
        u.interpolate(lambda x: (x[0], x[1]))
        write_function(u, file.with_suffix(suffix), encoder)
    MPI.COMM_WORLD.Barrier()
    mesh = read_mesh(MPI.COMM_WORLD, file.with_suffix(suffix), encoder, dolfinx.mesh.GhostMode.shared_facet)

    V = dolfinx.fem.FunctionSpace(mesh, ("N1curl", 1))
    u = dolfinx.fem.Function(V)
    read_function_perm(u, file.with_suffix(suffix), encoder)
    exit()
