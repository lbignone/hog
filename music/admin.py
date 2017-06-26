from django.contrib import admin
from .models import MusicGadgetIc, Seed, MusicEllipsoidRegion


class SeedInline(admin.TabularInline):
    model = Seed
    extra = 1


fieldsets = [(None, {'fields': ['name', ]}),
             ('Setup', {'fields': ['boxlength',
                                   'zstart',
                                   'region',
                                   'levelmin',
                                   'levelmax',
                                   'levelmin_TF',
                                   'force_equal_extent',
                                   'padding',
                                   'overlap',
                                   'blocking_factor',
                                   'align_top',
                                   'periodic_TF',
                                   'baryons',
                                   'use_2LPT',
                                   'use_LLA',
                                   'center_vel',
                                   ]}),
             ('Cosmology', {'fields': ['Omega_m',
                                       'Omega_L',
                                       'Omega_b',
                                       'H0',
                                       'sigma_8',
                                       'nspec',
                                       'transfer',
                                       'YHe',
                                       'gamma',
                                       ]}),
             ('Poisson', {'fields': ['laplace_order',
                                     'grad_order',
                                     'accuracy',
                                     'smoother',
                                     'pre_smooth',
                                     'post_smooth',
                                     'fft_fine'
                                     ]}), ]


class IcAdmin(admin.ModelAdmin):

    fieldsets += [('Output', {'fields': ['filename',
                                         'gadget_lunit',
                                         'gadget_munit',
                                         'gadget_vunit',
                                         'file_number',
                                         'gadget_coarsetype',
                                         'gadget_spreadcoarse',
                                         'gadget_longids',
                                         ]})]

    inlines = [SeedInline]


class EllipsoidAdmin(admin.ModelAdmin):
    pass


admin.site.register(MusicGadgetIc, IcAdmin)
admin.site.register(MusicEllipsoidRegion, EllipsoidAdmin)
