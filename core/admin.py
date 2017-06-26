from django.contrib import admin
from .models import EllipsoidRegion
import easy


class EllipsoidRegionAdmin(admin.ModelAdmin):

    raw_id_fields = ("structure",)
    fk1 = easy.ForeignKeyAdminField('structure')

    fieldsets = [
        (None, {'fields': ['name',
                           'structure',
                           'rtb',
                           ]
                }
         )
    ]


admin.site.register(EllipsoidRegion, EllipsoidRegionAdmin)
