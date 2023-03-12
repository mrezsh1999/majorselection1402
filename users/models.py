from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from booklet_information.models import Province


class NewUserManager(BaseUserManager):
    def create_user(self, mobile, password=None, **extra_fields):
        if not mobile:
            raise ValueError(_('The mobile number must be set'))
        user = self.model(mobile=mobile, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(mobile, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = None
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    mobile = models.CharField(_('mobile'), max_length=11, unique=True)
    # otp_key = models.CharField(_('otp_key'), max_length=64, null=True, blank=True)

    is_student = models.BooleanField(default=False)
    is_advisor = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)

    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = []

    objects = NewUserManager()

    backend = 'users.mybackend.MobileBackend'

    @property
    def name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.mobile


class Manager(User):
    pass

    class Meta:
        verbose_name = _('manager')
        verbose_name_plural = _('managers')

    def __str__(self):
        return self.name


class Advisor(User):
    manager_field = models.ForeignKey(Manager, on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        verbose_name = _('advisor')
        verbose_name_plural = _('advisors')

    def __str__(self):
        return self.name


# class School(models.Model):
#     title = models.CharField(max_length=64)
#     advisor = models.ManyToManyField(Advisor)
#
#     class Meta:
#         verbose_name = _('school')
#         verbose_name_plural = _('schools')
#
#     def __str__(self):
#         return self.title

class Student(User):
    FIELD_OF_STUDY = (
        (0, _('ریاضی')),
        (1, _('تجربی')),
        (2, _('انسانی')),
        (3, _('هنر')),
        (4, _('زبان'))
    )
    GENDER = (
        (True, _('مرد')),
        (False, _('زن'))
    )

    gender = models.BooleanField(choices=GENDER, null=True)
    national_code = models.CharField(max_length=10, null=True, blank=True, unique=True)
    field_of_study = models.PositiveSmallIntegerField(choices=FIELD_OF_STUDY, null=True, blank=True)
    volunteer_code = models.IntegerField(null=True, blank=True)

    province = models.ForeignKey(Province, on_delete=models.PROTECT, null=True, blank=True)
    student_advisor = models.ForeignKey(Advisor, on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        verbose_name = _('student')
        verbose_name_plural = _('students')

    def __str__(self):
        return self.name


class ReportCard(models.Model):
    report_card_file = models.FileField(upload_to='report_card_file')
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name='report_card', null=True)

    def __str__(self):
        return self.student.name

    class Meta:
        verbose_name = _('report card')
        verbose_name_plural = _('report cards')