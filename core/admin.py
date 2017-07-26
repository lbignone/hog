from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from .models import EllipsoidRegion, Structure, BoxRegion, Category
import easy
import numpy as np


def set_region_point_file(modeladmin, request, queryset):
    import core
    for obj in queryset:
        core.utils.set_region_point_file(obj)
        core.utils.compute_ellipsoid(obj)


def compute_ellipsoid(modeladmin, request, queryset):
    import core
    for obj in queryset:
        core.utils.compute_ellipsoid(obj)


def compute_N(modeladmin, request, queryset):
    for obj in queryset:
        fname = obj.get_point_filename()
        part = np.genfromtxt(fname)
        obj.N = len(part)
        obj.save()


class EllipsoidRegionAdmin(admin.ModelAdmin):

    list_display = ('id',
                    'structure',
                    'rtb',
                    'rvir',
                    'N',
                    'region_point_file',
                    'xc',
                    'yc',
                    'zc',
                    'V',
                    'V_norm',
                    'a',
                    'b',
                    'c',

                    )

    raw_id_fields = ("structure",)
    fk1 = easy.ForeignKeyAdminField('structure')

    fieldsets = [
        (None, {'fields': ['name',
                           'category', 
                           'structure',
                           'rtb',
                           ]
                }
         )
    ]

    actions = [set_region_point_file, compute_ellipsoid, compute_N]
    list_filter = ('category', 'rtb')


class StructureRegionAdmin(admin.ModelAdmin):

    list_filter = ('catalogue__snapshot', )


admin.site.register(EllipsoidRegion, EllipsoidRegionAdmin)
admin.site.register(BoxRegion)
admin.site.register(Structure, StructureRegionAdmin)
admin.site.register(Category, DraggableMPTTAdmin)
