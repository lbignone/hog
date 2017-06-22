from django.contrib import admin
from .models import GadgetIc, Seed


class SeedInline(admin.TabularInline):
    model = Seed
    extra = 1


class IcAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', ]}),
        ('Setup', {'fields': ['boxlength',
                              'zstart',
                              # 'region',
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
        ('Output', {'fields': ['filename',
                               'gadget_lunit',
                               'gadget_munit',
                               'gadget_vunit',
                               'gadget_num_files',
                               'gadget_coarsetype',
                               'gadget_spreadcoarse',
                               'gadget_longids',
                               ]}),
        ('Poisson', {'fields': ['laplace_order',
                                'grad_order',
                                'accuracy',
                                'smoother',
                                'pre_smooth',
                                'post_smooth',
                                'fft_fine'
                                ]}),
    ]

    inlines = [SeedInline]


admin.site.register(GadgetIc, IcAdmin)
