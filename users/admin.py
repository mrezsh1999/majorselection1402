from django.contrib import admin
from django import forms
from django.utils.translation import gettext_lazy as _
from booklet_information.models import Province
from users.models import User, Student, Advisor, Manager, ReportCard, School




class UserAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, UserAdmin)


class StudentAdmin(admin.ModelAdmin):
    model = User
    list_display = ['name', 'mobile',
                    'national_code', 'gender', 'field_of_study']
    list_filter = ['field_of_study', 'gender']
    search_fields = ['name', 'mobile', 'national_code']
    fieldsets = (
        (_('Personal info'),
         {'fields': (
             'first_name', 'last_name', 'mobile', 'is_student', 'gender', 'national_code', 'province',
             'volunteer_code')}),
        (_('Educational info'), {
            'fields': ('field_of_study', 'student_advisor', 'school')}),
        (_('State'),
         {'fields': ('is_state_choose_default', 'is_state_choose_booklet_rows_done',
                     'is_state_final_approval', 'process_start_time', 'process_end_time')})
    )


admin.site.register(Student, StudentAdmin)


class AdvisorAdmin(admin.ModelAdmin):
    fieldsets = (
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'mobile', 'is_advisor')}),
        (_('Institute info'), {'fields': ('manager_field',)})
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if not change: 
            for i in range(4):
                student = Student.objects.create(
                    first_name='دانش آموز {}'.format(i+1),
                    last_name='{}'.format(obj.name),
                    mobile=int(obj.mobile) + i+1,
                    student_advisor=obj,
                    gender=True if i % 2 == 1 else False,
                    field_of_study=0,
                    is_student=True,
                    province=Province.objects.get(id=8),
                )
                student.save()


admin.site.register(Advisor, AdvisorAdmin)


class ManagerAdmin(admin.ModelAdmin):
    model = User
    fieldsets = (
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'mobile', 'is_manager')}),
    )


admin.site.register(Manager, ManagerAdmin)


class ReportCardAdmin(admin.ModelAdmin):
    pass


admin.site.register(ReportCard, ReportCardAdmin)

class SchoolAdmin(admin.ModelAdmin):
    pass


admin.site.register(School, SchoolAdmin)
