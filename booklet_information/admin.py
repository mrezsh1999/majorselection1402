from django.contrib import admin

from booklet_information.models import Province, Major, University, BookletRow, SelectProvince, SelectProvinceForMajor, \
    SelectDefaultProvince, SelectDefaultMajor, MajorSelection


class ProvinceAdmin(admin.ModelAdmin):
    search_fields = ['title']


admin.site.register(Province, ProvinceAdmin)


class MajorAdmin(admin.ModelAdmin):
    list_display = ['title', 'field_of_study']
    list_filter = ['field_of_study']
    search_fields = ['title']


admin.site.register(Major, MajorAdmin)


class UniversityAdmin(admin.ModelAdmin):
    raw_id_fields = ('province',)
    list_display = ['title', 'province', 'rank']
    list_filter = ['province']
    search_fields = ['title', 'province__title']


admin.site.register(University, UniversityAdmin)


class BookletRowAdmin(admin.ModelAdmin):
    raw_id_fields = ('university', 'major')
    list_display = ['university', 'major', 'exam_based', 'course']
    list_filter = ['exam_based', 'course', 'major__field_of_study']
    search_fields = ['university__title', 'major__title', 'major_code']


admin.site.register(BookletRow, BookletRowAdmin)


class SelectProvinceAdmin(admin.ModelAdmin):
    list_display = ['index', 'province']


admin.site.register(SelectProvince, SelectProvinceAdmin)


class SelectProvinceForMajorAdmin(admin.ModelAdmin):
    raw_id_fields = ('student', 'major')
    list_display = ['index', 'student', 'major', 'get_select_province']
    search_fields = ['student__first_name', 'student__last_name', 'major__title']

    def get_select_province(self, obj):
        return " - ".join([p.province.title for p in obj.select_province.all()])


admin.site.register(SelectProvinceForMajor, SelectProvinceForMajorAdmin)


class SelectDefaultProvinceAdmin(admin.ModelAdmin):
    raw_id_fields = ('student', 'province')
    list_display = ['index', 'student', 'province']
    list_filter = ['province']
    search_fields = ['student__first_name', 'student__last_name', 'province__title']


admin.site.register(SelectDefaultProvince, SelectDefaultProvinceAdmin)


class SelectDefaultMajorAdmin(admin.ModelAdmin):
    raw_id_fields = ('student', 'major')
    list_display = ['index', 'student', 'major']
    search_fields = ['student__first_name', 'student__last_name', 'major__title']


admin.site.register(SelectDefaultMajor, SelectDefaultMajorAdmin)


class MajorSelectionAdmin(admin.ModelAdmin):
    raw_id_fields = ('booklet_row', 'student')
    ordering = ['rank']
    list_display = ['rank', 'booklet_row', 'student']
    list_filter = ['student']


admin.site.register(MajorSelection, MajorSelectionAdmin)
