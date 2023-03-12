from django.contrib import admin
from django import forms
from django.utils.translation import gettext_lazy as _

from users.models import User, Student, Advisor, Manager, ReportCard


class UserAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, UserAdmin)


class StudentAdmin(admin.ModelAdmin):
    model = User
    list_display = ['name', 'mobile', 'national_code', 'gender', 'field_of_study']
    list_filter = ['field_of_study', 'gender']
    search_fields = ['name', 'mobile', 'national_code']
    fieldsets = (
        (_('Personal info'),
         {'fields': ('first_name', 'last_name', 'mobile', 'is_student', 'gender', 'national_code', 'province')}),
        (_('Educational info'), {'fields': ('field_of_study', 'quota', 'quota_of_regions', 'student_advisor')}),
        # (_('State'), {'fields': ('is_answered', 'under_investigation', 'is_confirmed', 'finalized')}),
        # (_('State experimental/math/humanities'), {'fields': (
        #     'is_teachers', 'is_yes_test', 'is_nightly', 'self_governing_campus', 'is_no_test', 'free_self_government',
        #     'free_all_the_time', 'tuition_fee')}),
    )


admin.site.register(Student, StudentAdmin)


class AdvisorAdmin(admin.ModelAdmin):
    model = User
    fieldsets = (
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'mobile', 'is_advisor')}),
        (_('Institute info'), {'fields': ('manager_field',)})
    )


admin.site.register(Advisor, AdvisorAdmin)


class ManagerAdmin(admin.ModelAdmin):
    model = User
    fieldsets = (
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'mobile', 'is_manager')}),
    )


admin.site.register(Manager, ManagerAdmin)


class ReportCardAdmin(admin.ModelAdmin):
    pass


admin.site.register(ReportCard, ReportCardAdmin)