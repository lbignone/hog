import numpy as np


def get_region_in_radius(halo, radius):
    """
    Get the spherical region centered around a halo

    Parameters
    ----------
    halo : RockstarHalo
        halo
    radius : float, distance quantity
        radius in length units

    Returns
    -------
        region

    """
    snapshot = halo.catalogue.snapshot
    catalogue = halo.catalogue

    unit_length = catalogue.unit_length

    centre = np.array([halo.x, halo.y, halo.z])
    centre *= unit_length

    reg = snapshot.get_region_in_radius(centre, radius)

    return reg
