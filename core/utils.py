import os
import errno
import numpy as np


def makedirs(name):
    """Makes directory if it does not already exists."""
    try:
        os.makedirs(name)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def get_lagrangian_volume(structure, radius):
    """
    Obtain the positions of the particles occupying the lagrangian volume
    corresponding to a spherical region center around a structure.

    Parameters
    ----------
    structure : structure_like
        structure at the center of the spherical volume.
    radius : distance_quantity
        search radius.

    Returns
    -------
    array_like
        position array in units of the box length.

    """

    simulation = structure.catalogue.snapshot.simulation

    ic = simulation.ic

    reg = structure.get_region_in_radius(radius)

    pos = ic.get_pos_by_region(reg)
    pos /= simulation.get_box_length()

    return pos


def get_lagrangian_by_rtb(structure, rtb):
    """
    Obtain the positions of the particles occupying the lagrangian volume
    corresponding to a spherical region center around a structure. The search
    radius is rtb times the structure radius.

    Parameters
    ----------
    structure : structure_like
        structure at the center of the spherical volume.
    rtb : float
        the search radius is rtb times the structure radius.

    Returns
    -------
    array_like
        position array in units of the box length.

    """

    radius = structure.get_radius() * rtb

    pos = get_lagrangian_volume(structure, radius)

    return pos


def region_filename(region, filename):
    """
    Obtain the region point filename. This function is mainly to be used with
    the FileFild.

    """
    fname = region.get_point_filename()
    return fname


def save_region_point_file(region, pos):
    """
    Save the positions array to the region point file. If the folder
    corresponding to the region does not exists it creates it.

    Parameters
    ----------
    region : region_like
        the region described by the particle positions.
    pos : array_like
        the positions.

    Returns
    -------
    string
        the full path to the region point file.
    """
    path = region.get_path()

    makedirs(path)

    fname = region_filename(region, None)

    np.savetxt(fname, pos, fmt='%-12.4f')

    return fname


def create_ellipsoid_region(structure, rtb):
    """
    Create an ellipsoid region center around a structure

    Parameters
    ----------
    structure : structure_like
        structure at the center of the spherical volume.
    rtb : float
        the search radius is rtb times the structure radius.

    Returns
    -------
    region_like
        EllipsoidRegion.
    """
    from core.models import EllipsoidRegion

    region = EllipsoidRegion()
    region.structure = structure
    region.rtb = rtb
    set_region_point_file(region)

    return region


def compute_ellipsoid(reg):
    from subprocess import check_output

    fname = reg.get_point_filename()

    r = check_output(['ellipsoid', fname])

    r = r.splitlines()

    A = [[float(t) for t in (r[3].split(b'=')[1].split(b','))],
         [float(t) for t in (r[4].split(b'=')[1].split(b','))],
         [float(t) for t in (r[5].split(b'=')[1].split(b','))],
         ]

    A = np.array(A)

    reg.A_arr = A

    a, b, c = (np.linalg.eigvals(A))**(-0.5)

    V = (4. / 3) * np.pi * a * b * c

    structure = reg.structure
    snapshot = structure.catalogue.snapshot
    sim = snapshot.simulation
    rvir = structure.get_radius().to(sim.unit_length)
    Vn = (4. / 3) * np.pi * rvir**3
    reg.V_norm = V * sim.get_box_length()**3 / Vn

    reg.V = V
    reg.a = a
    reg.b = b
    reg.c = c

    xc, yc, zc = [float(t) for t in (r[6].split(b'=')[1].split(b','))]
    reg.xc = xc
    reg.yc = yc
    reg.zc = zc

    # from music.plot_ellipsoid import plot_ellipsoid
    # import matplotlib.pyplot as plt
    # from mpl_toolkits.mplot3d import Axes3D

    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')
    # plot_ellipsoid([xc, yc, zc], A, ax, c='b')
    # img_fname = abs_path + str(self.id) + "_" + self.name + ".svg"
    # plt.savefig(img_fname)

    reg.save()

    return r


def set_region_point_file(region):
    """
    Set the region point file based on model data.
    """
    structure = region.structure
    rtb = region.rtb
    pos = get_lagrangian_by_rtb(structure, rtb)

    region.name = str(structure)
    region.snapshot = structure.catalogue.snapshot
    region.structure = structure
    region.N = len(pos)
    region.save()

    fname = save_region_point_file(region, pos)
    region.region_point_file = fname

    region.save()
