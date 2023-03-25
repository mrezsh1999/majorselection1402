from django.contrib import admin

from booklet_information.models import Province, Major, University, BookletRow, SelectProvince, SelectProvinceForMajor, \
    SelectDefaultProvince, SelectDefaultMajor, MajorSelection


class ProvinceAdmin(admin.ModelAdmin):
    pass


admin.site.register(Province, ProvinceAdmin)


class MajorAdmin(admin.ModelAdmin):
    pass


admin.site.register(Major, MajorAdmin)


class UniversityAdmin(admin.ModelAdmin):
    pass


admin.site.register(University, UniversityAdmin)


class BookletRowAdmin(admin.ModelAdmin):
    raw_id_fields = ('university', 'major')
    list_display = ['university', 'major', 'exam_based', 'course']
    list_filter = ['exam_based', 'course', 'major__field_of_study']
    search_fields = ['university__title', 'major__title', 'major_code']


admin.site.register(BookletRow, BookletRowAdmin)


class SelectProvinceAdmin(admin.ModelAdmin):
    pass


admin.site.register(SelectProvince, SelectProvinceAdmin)


class SelectProvinceForMajorAdmin(admin.ModelAdmin):
    pass


admin.site.register(SelectProvinceForMajor, SelectProvinceForMajorAdmin)


class SelectDefaultProvinceAdmin(admin.ModelAdmin):
    pass


admin.site.register(SelectDefaultProvince, SelectDefaultProvinceAdmin)


class SelectDefaultMajorAdmin(admin.ModelAdmin):
    pass


admin.site.register(SelectDefaultMajor, SelectDefaultMajorAdmin)


class MajorSelectionAdmin(admin.ModelAdmin):
    raw_id_fields = ('booklet_row', 'student')
    ordering = ['rank']
    list_display = ['rank', 'booklet_row', 'student']
    list_filter = ['student']


admin.site.register(MajorSelection, MajorSelectionAdmin)
