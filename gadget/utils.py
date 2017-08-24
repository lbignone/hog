from scipy.spatial.ckdtree import cKDTree
from gadget import pygadget


def get_pygadget_sim(snapshot, is_IC=False):
    """
    Get pygadget.Simulation instance corresponding to the snapshot.

    Parameters
    ----------
    snapshot : snapshot_like
        snapshot.
    is_IC : bool, optional
        whether or not is an initial condition snapshot.

    Returns
    -------
    pygadgetSimulation.

    """

    fname = snapshot.fname

    file_number = snapshot.file_number

    multiple_files = file_number != 1

    if not is_IC:
        simulation = snapshot.simulation
        pot = simulation.pot
        accel = simulation.accel
        endt = simulation.endt
        tstp = simulation.tstp
    else:
        pot = False
        accel = False
        endt = False
        tstp = False

    sim = pygadget.Simulation(fname, multiple_files=multiple_files,
                              pot=pot, accel=accel, endt=endt, tstp=tstp)

    return sim


def read_block(snapshot, block_type, particle_type, is_IC=False):
    """
    Reads a block from the snapshot file.

    Parameters
    ----------
    snapshot : snapshot_like
        snapshot.
    block_type : string
        block type
    particle_type : string
        particle type.
    is_IC : bool, optional
        whether or not is an initial condition snapshot.

    Returns
    -------
    block in pygadget format.

    """
    file_number = snapshot.file_number

    multiple_files = file_number != 1

    sim = get_pygadget_sim(snapshot, is_IC=is_IC)

    block = sim.read_block(block_type, particle_type,
                           iter_files=multiple_files)

    # put pos in a list so the following iterarion works also in sigle file
    # snapshots
    if multiple_files:
        pass
    else:
        block = [block, ]

    return block


def search_sorting(block, ids):
    """
    Returns the block information limited to selected ids.
    It first sorts the ids for faster computation.

    """
    ids = list(ids)
    index = block.index
    sorter = index.argsort()
    ind = index.searchsorted(ids, sorter=sorter)

    return block.iloc[sorter].iloc[ind]


def get_pos_from_ids(snapshot, ids):
    """
    Return the positions for selected ids.

    """
    file_number = snapshot.file_number

    ids = set(ids)

    pos = snapshot.read_block("pos", "halo")

    # with ProgressBar(file_number) as bar:
    first = True
    for p in pos:
        if file_number == 1:
            det_ind = ids
        else:
            ind = set(p.index)
            det_ind = ind.intersection(ids)
        if (len(det_ind) > 0):
            if first:
                det_pos = search_sorting(p, det_ind)
                first = False
            else:
                det_pos = det_pos.append(search_sorting(p, det_ind))

            if len(ids) == len(det_pos):
                break

        # bar.update()

    return det_pos.copy()


def get_region_in_radius(snapshot, centre, radius, n_jobs=1):
    """
    Returns the ids of particles located in a spherical region.

    Parameters
    ----------
    snapshot : snapshot_like
        snapshot.
    centre : array_like, distance quantity
        center of the spherical region in cartesian coordinates.
        In unit distance.
    radius : float, distance quantity
        radius of the spherical region in unit distance

    Returns
    -------
    array_like
        particle ids.

    """
    simulation = snapshot.simulation

    pos = snapshot.read_block("pos", "halo")

    radius = radius.to(simulation.unit_length)
    centre = centre.to(simulation.unit_length)

    first = True
    for p in pos:
        tree = cKDTree(p.values, boxsize=simulation.boxlength)

        ind = tree.query_ball_point(centre.value, radius.value, n_jobs=n_jobs)
        if first:
            ids = p.iloc[ind].index
            if len(ids) > 0:
                first = False
        else:
            ids = ids.append(p.iloc[ind].index)

    return ids.copy()
