from scipy.spatial.ckdtree import cKDTree
from gadget import pygadget
from django.db import models
from core.utils import makedirs
import os


module_dir = os.path.dirname(__file__)


makefile_options = ['PERIODIC',
                    'UNEQUALSOFTENINGS',
                    'PEANOHILBERT',
                    'WALLCLOCK',
                    'PMGRID',
                    'PLACEHIGHRESREGION',
                    'ENLARGEREGION',
                    'ASMTH',
                    'RCUT',
                    'DOUBLEPRECISION',
                    'DOUBLEPRECISION_FFTW',
                    'SYNCHRONIZATION',
                    'FLEXSTEPS',
                    'PSEUDOSYMMETRIC',
                    'NOSTOP_WHEN_BELOW_MINTIMESTEP',
                    'NOPMSTEPADJUSTMENT',
                    'HAVE_HDF5',
                    'OUTPUTPOTENTIAL',
                    'OUTPUTACCELERATION',
                    'OUTPUTCHANGEOFENTROPY',
                    'OUTPUTTIMESTEP',
                    'LONGIDS',]

parameter_options = [
                        'OutputDir',
                        'SnapshotFileBase',
                        'SnapFormat',
                        'NumFilesPerSnapshot',
                        'BoxSize',
                        'PeriodicBoundariesOn',
                        'ComovingIntegrationOn',
                        'HubbleParam',
                        'Omega0',
                        'OmegaLambda',
                        # 'OmegaBaryon',
                        'BufferSize',
                        'PartAllocFactor',
                        'TreeAllocFactor',
                        'TypeOfOpeningCriterion',
                        'ErrTolTheta',
                        'ErrTolForceAcc',
                        'MaxSizeTimestep',
                        'MinSizeTimestep',
                        'TypeOfTimestepCriterion',
                        'ErrTolIntAccuracy',
                        'TreeDomainUpdateFrequency',
                        'MaxRMSDisplacementFac',
                        'OutputListOn',
                        'OutputListFilename',
                        'TimeOfFirstSnapshot',
                        'TimeBetSnapshot',
                        'TimeBetStatistics',
                        'NumFilesWrittenInParallel',
                        'UnitVelocity_in_cm_per_s',
                        'UnitLength_in_cm',
                        'UnitMass_in_g',
                        'GravityConstantInternal',
                        'DesNumNgb',
                        'MaxNumNgbDeviation',
                        'ArtBulkViscCons',
                        'CourantFac',
                        'InitGasTemp',
                        'MinGasTemp',
                        'MinGasHsmlFractional',
                        'SofteningGas',
                        'SofteningHalo',
                        'SofteningDisk',
                        'SofteningBulge',
                        'SofteningStars',
                        'SofteningBndry',
                        'SofteningGasMaxPhys',
                        'SofteningHaloMaxPhys',
                        'SofteningDiskMaxPhys',
                        'SofteningBulgeMaxPhys',
                        'SofteningStarsMaxPhys',
                        'SofteningBndryMaxPhys',
                    ]


def parameter_name(parameter):
    new_names = {'SnapshotFileBase': 'snapshot_file_base',
                 'NumFilesPerSnapshot': 'file_number',
                 'BoxSize': 'boxlength',
                 'HubbleParam': 'h',
                 'Omega0': 'Omega_m',
                 'OmegaLambda': 'Omega_l',
                 'UnitVelocity_in_cm_per_s': 'velocity_in_cm_per_s',
                 'UnitLength_in_cm': 'length_in_cm',
                 'UnitMass_in_g': 'mass_in_g',
                }
    if parameter in new_names:
        return new_names[parameter]
    else:
        return parameter


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
        pot = simulation.OUTPUTPOTENTIAL
        accel = simulation.OUTPUTACCELERATION
        endt = simulation.OUTPUTCHANGEOFENTROPY
        tstp = simulation.OUTPUTTIMESTEP
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


def save_makefile(gadget_run, template='makefile.template'):

    path = gadget_run.get_path()
    makedirs(path)

    template_path = os.path.join(module_dir, template)

    with open(template_path, 'r') as f:
        content = f.read()

    values = {}
    for option in makefile_options:
        field = getattr(gadget_run, option)
        
        value = '#OPT   +=   -D' + option
        
        if field is not None:
        
            if type(field) != bool:
                value += '=' + str(field)
            if field:
                value = value[1:]
        
        values[option] = value
    
    content = content.format(**values)

    fname = gadget_run.get_makefile_path()
    with open(fname, 'w') as f:
        f.write(content)


def save_config(gadget_run):
    path = gadget_run.get_path()
    makedirs(path)

    content = ''
    for option in parameter_options:
        field_name = parameter_name(option)
        field = getattr(gadget_run, field_name)
        content += "{:<30}".format(option) + str(field) + '\n'

    fname = gadget_run.get_config_path()
    with open(fname, 'w') as f:
        f.write(content)


def save_pbs_file(gadget_run, template='geryon.pbs', nodes=1, ppn=40, walltime='72:00:00'):

    path = gadget_run.get_path()
    fname = gadget_run.get_config_path()
    name = fname.split('.')[0]
    name = name.split('/')[-1]
       
    fpbs = path + name + '.pbs'
    gadget_conf = name + '.param'

    template_path = os.path.join(module_dir, template)

    with open(template_path, 'r') as f_template:
        template = f_template.read()
    
    template = template.format(name=name,
                               nodes=nodes,
                               ppn=ppn,
                               walltime=walltime,
                               gadget_conf=gadget_conf,
                               )

    with open(fpbs, 'w') as fout:
        fout.write(template)
