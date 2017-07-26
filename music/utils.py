from core.utils import makedirs
from django.db import transaction


def bool_to_string(bool_value):
    if bool_value:
        return 'yes'
    else:
        return 'no'


def option_formatter(value, fmt):
    if value is None:
        return None

    if fmt == 'bool':
        out = bool_to_string(value)
    else:
        out = fmt.format(value)

    return out


def out_option_list(option_list):
    output = ''
    for option in option_list:
        value = option_formatter(option[1], option[2])
        if value:
            output += option[0] + ' = ' + value + '\n'

    return output


def gadget_output_list(ic):

    output_list = [
        ('gadget_lunit', ic.gadget_lunit, '{:s}'),
        ('gadget_munit', ic.gadget_munit, '{:s}'),
        ('gadget_vunit', ic.gadget_vunit, '{:s}'),
        ('gadget_num_files', ic.gadget_num_files, '{:d}'),
        ('gadget_coarsetype', ic.gadget_coarsetype, '{:d}'),
        ('gadget_spreadcoarse', ic.gadget_spreadcoarse, 'bool'),
        ('gadget_longids', ic.gadget_longids, 'bool'),
    ]

    return output_list


def config_output(ic):

    setup_list = [
        ('boxlength', ic.boxlength, '{:.1f}'),
        ('zstart', ic.zstart, '{:.1f}'),
        ('region', ic.region.region_type, '{:s}'),
        ('levelmin', ic.levelmin, '{:d}'),
        ('levelmax', ic.levelmax, '{:d}'),
        ('levelmin_TF', ic.levelmin_TF, '{:d}'),
        ('force_equal_extent', ic.force_equal_extent, 'bool'),
        ('padding', ic.padding, '{:d}'),
        ('overlap', ic.overlap, '{:d}'),
        ('blocking_factor', ic.blocking_factor, '{:d}'),
        ('align_top', ic.align_top, 'bool'),
        ('periodic_TF', ic.periodic_TF, 'bool'),
        ('baryons', ic.baryons, 'bool'),
        ('use_2LPT', ic.use_2LPT, 'bool'),
        ('use_LLA', ic.use_LLA, 'bool'),
        ('center_vel', ic.center_vel, 'bool'),
    ]

    if ic.region.region_type == 'ellipsoid':
        region_list = [
            ('region_point_file', ic.region.region_point_file, '{:s}'),
            ('region_point_shift', ic.region.region_point_shift, '{:s}'),
            ('region_point_levelmin', ic.region.region_point_levelmin, '{:s}'),
        ]

    elif ic.region.region_type == 'box':
        region_list = [
            ('ref_offset', ic.region.ref_offset, '{:s}'),
            ('ref_center', ic.region.ref_center, '{:s}'),
            ('ref_extent', ic.region.ref_extent, '{:s}'),
            ('ref_dims', ic.region.ref_dims, '{:s}'),
        ]

    cosmology_list = [
        ('Omega_m', ic.Omega_m, '{:.3f}'),
        ('Omega_L', ic.Omega_L, '{:.3f}'),
        ('Omega_b', ic.Omega_b, '{:.3f}'),
        ('H0', ic.H0, '{:.3f}'),
        ('sigma_8', ic.sigma_8, '{:.3f}'),
        ('nspec', ic.nspec, '{:.3f}'),
        ('transfer', ic.transfer, '{:s}'),
        ('YHe', ic.YHe, '{:.3f}'),
        ('gamma', ic.gamma, '{:.3f}'),
    ]

    from music.models import Seed

    seed = Seed.objects.filter(ic=ic)

    seed_list = []
    for s in seed:
        seed_list += (('seed[{:d}]'.format(s.level), s.value, '{:d}'),)

    output_list = [
        ('format', ic.output_format, '{:s}'),
        ('filename', ic.filename, '{:s}'),
    ]

    output_list += ic.output_list()

    poisson_list = [
        ('laplace_order', ic.laplace_order, '{:d}'),
        ('grad_order', ic.grad_order, '{:d}'),
        ('accuracy', ic.accuracy, '{:e}'),
        ('smoother', ic.smoother, '{:s}'),
        ('pre_smooth', ic.pre_smooth, '{:d}'),
        ('post_smooth', ic.post_smooth, '{:d}'),
        ('fft_fine', ic.fft_fine, 'bool'),
    ]

    output = '[setup]\n'
    output += out_option_list(setup_list)
    output += out_option_list(region_list)

    output += '\n[cosmology]\n'
    output += out_option_list(cosmology_list)

    output += '\n[random]\n'
    output += out_option_list(seed_list)

    output += '\n[output]\n'
    output += out_option_list(output_list)

    output += '\n[poisson]\n'
    output += out_option_list(poisson_list)

    return output


def save_config_file(ic):
    output = config_output(ic)

    path = ic.get_path()
    makedirs(path)

    fname = ic.get_config_filename()

    with open(fname, 'w') as fout:
        fout.write(output)


@transaction.atomic
def create_ic_from_existing(ic):
    from .admin import fieldsets, gadget_fieldsets
    from .models import MusicGadgetIc
    from music.models import Seed

    fieldsets = fieldsets + gadget_fieldsets

    new_ic = MusicGadgetIc()

    for group in fieldsets:
        for field in group[1]['fields']:
            if field == 'category':
                continue
            setattr(new_ic, field, getattr(ic, field))

    new_ic.save()

    seeds = ic.seed_set.all()
    for seed in seeds:
        new_seed = Seed(ic=new_ic, level=seed.level, value=seed.value)
        new_seed.save()

    return new_ic
