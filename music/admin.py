from django.contrib import admin
from .models import MusicGadgetIc, Seed
from .models import MusicBoxRegion, MusicEllipsoidRegion
from mptt.admin import TreeRelatedFieldListFilter
import easy


def save_config_file(modeladmin, request, queryset):
    from .utils import save_config_file
    for obj in queryset:
        save_config_file(obj)


class SeedInline(admin.TabularInline):
    model = Seed
    extra = 1


fieldsets = [(None, {'fields': ['name', 'category']}),
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

gadget_fieldsets = [('Output', {'fields': ['filename',
                                           'gadget_lunit',
                                           'gadget_munit',
                                           'gadget_vunit',
                                           'file_number',
                                           'gadget_coarsetype',
                                           'gadget_spreadcoarse',
                                           'gadget_longids',
                                           ]})]


class IcAdmin(admin.ModelAdmin):

    raw_id_fields = ("region",)
    fk1 = easy.ForeignKeyAdminField('region')

    actions = [save_config_file, ]

    fieldsets += gadget_fieldsets

    inlines = [SeedInline]

    list_display = ('id',
                    'name',
                    'boxlength',
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
                    'Omega_m',
                    'Omega_L',
                    'Omega_b',
                    'H0',
                    'sigma_8',
                    'nspec',
                    'transfer',
                    'YHe',
                    'gamma',
                    'laplace_order',
                    'grad_order',
                    'accuracy',
                    'smoother',
                    'pre_smooth',
                    'post_smooth',
                    'fft_fine',
                    'filename',
                    'gadget_lunit',
                    'gadget_munit',
                    'gadget_vunit',
                    'file_number',
                    'gadget_coarsetype',
                    'gadget_spreadcoarse',
                    'gadget_longids',
                    )
    list_filter = ('baryons', 'levelmin', 'levelmax', 'region')
    search_fields = ['name', 'id']


admin.site.register(MusicGadgetIc, IcAdmin)
admin.site.register(MusicEllipsoidRegion)
admin.site.register(MusicBoxRegion)
