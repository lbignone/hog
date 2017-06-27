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


def set_region_point_file(region):
    """
    Set the region point file based on model data.
    """
    structure = region.structure
    rtb = region.rtb
    pos = get_lagrangian_by_rtb(structure, rtb)
    region.N = len(pos)

    region.name = str(structure)
    region.snapshot = structure.catalogue.snapshot
    region.structure = structure
    region.save()

    fname = save_region_point_file(region, pos)
    region.region_point_file = fname

    region.save()


def compute_ellipsoid(region):

        fname = region.get_point_filename()

        from subprocess import check_output

        cmd = ['ellipsoid', fname, ]

        r = check_output(cmd)

        r = r.splitlines()

        A = [
            [float(t) for t in (r[3].split('=')[1].split(','))],
            [float(t) for t in (r[4].split('=')[1].split(','))],
            [float(t) for t in (r[5].split('=')[1].split(','))]
        ]
        A = np.array(A)

        region.A_arr = A

        a, b, c = (np.linalg.eigvals(A))**(-0.5)

        V = (4. / 3) * np.pi * a * b * c

        structure = region.structure
        rvir = structure.get_radius()
        Vn = (4. / 3) * np.pi * rvir**3

        simulation = structure.catalogue.snapshot.simulation
        box_length = simulation.get_box_length()

        V_norm = V * box_length**3 / Vn
        V_norm = V_norm.decompose()

        region.V_norm = V_norm

        region.V = V
        region.a = a
        region.b = b
        region.c = c

        xc, yc, zc = [float(t) for t in (r[6].split('=')[1].split(','))]
        region.xc = xc
        region.yc = yc
        region.zc = zc

        region.save()

        return r
