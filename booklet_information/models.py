from django.db import models, transaction
from django.utils.translation import gettext_lazy as _


class Province(models.Model):
    title = models.CharField(max_length=32)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Province")
        verbose_name_plural = _("Provinces")


class Major(models.Model):
    FIELD_OF_STUDY = (
        (0, _("ریاضی")),
        (1, _("تجربی")),
        (2, _("انسانی")),
        (3, _("هنر")),
        (4, _("زبان")),
        (5, _("ریاضی 1")),
        (6, _("ریاضی و فیزیک")),
        (7, _("ریاضی جدید")),
    )

    title = models.CharField(max_length=512)
    field_of_study = models.PositiveSmallIntegerField(choices=FIELD_OF_STUDY, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Major")
        verbose_name_plural = _("Majors")


class University(models.Model):
    title = models.CharField(max_length=512)
    province = models.ForeignKey(Province, on_delete=models.PROTECT)
    rank = models.PositiveSmallIntegerField(blank=True, null=True)
    rank_riazi = models.PositiveSmallIntegerField(blank=True, null=True)
    rank_tajrobi = models.PositiveSmallIntegerField(blank=True, null=True)
    rank_ensani = models.PositiveSmallIntegerField(blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("University")
        verbose_name_plural = _("Universities")


class BookletRow(models.Model):
    DAILY = 0
    NIGHTLY = 1
    PARDIS = 2
    SHAHRIEPARDAZ = 3
    PAYAMNOOR = 4
    GHEIRENTEFAEI = 5
    MAJAZI = 6
    KHODGARDANAZAD = 7
    AZADTAMAMVAGHT = 8
    FARHANGIAN = 9
    BOMI = 10
    BOURSIE = 11
    BEHYARI = 12

    COURSE = (
        (DAILY, _("روزانه")),
        (NIGHTLY, _("نوبت دوم")),
        (PARDIS, _("پردیس خودگردان")),
        (SHAHRIEPARDAZ, _("شهریه پرداز")),
        (PAYAMNOOR, _("پیام نور")),
        (GHEIRENTEFAEI, _("غیر انتفاعی")),
        (MAJAZI, _("مجازی")),
        (KHODGARDANAZAD, _("خودگردان آزاد")),
        (AZADTAMAMVAGHT, _("آزاد تمام وقت")),
        (FARHANGIAN, _("فرهنگیان")),
        (BOMI, _("بومی")),
        (BOURSIE, _("بورسیه")),
        (BEHYARI, _("بهیاری")),
    )

    GENDER = (
        (0, _("دختر")),
        (1, _("پسر")),
        (2, _("هردو")),
    )

    ADMISSION = (
        (0, _("اول")),
        (1, _("دوم")),
    )

    EXAM_BASE = ((True, _("با آزمون")), (False, _("صرفا با سوابق تحصیلی")))

    major_code = models.IntegerField(default=0)
    exam_based = models.BooleanField(choices=EXAM_BASE, default=True)
    course = models.PositiveSmallIntegerField(choices=COURSE, default=0)
    gender = models.PositiveSmallIntegerField(choices=GENDER, default=0)
    admission = models.PositiveSmallIntegerField(choices=ADMISSION, default=0)

    university = models.ForeignKey(University, on_delete=models.PROTECT)
    major = models.ForeignKey(Major, on_delete=models.PROTECT)

    boursie_description = models.CharField(max_length=512, blank=True, null=True)

    def __str__(self):
        return "{} {}".format(self.major.title, self.university.title)

    class Meta:
        verbose_name = _("BookletRow")
        verbose_name_plural = _("BookletRows")


class SelectProvince(models.Model):
    index = models.PositiveSmallIntegerField()
    province = models.ForeignKey(
        Province, on_delete=models.PROTECT, null=True, blank=True
    )

    class Meta:
        ordering = ("index",)


class SelectProvinceForMajor(models.Model):
    index = models.PositiveSmallIntegerField()
    student = models.ForeignKey(
        "users.Student", on_delete=models.PROTECT, null=True, blank=True
    )
    major = models.ForeignKey(Major, on_delete=models.PROTECT, null=True, blank=True)
    select_province = models.ManyToManyField(SelectProvince)


class SelectDefaultProvince(models.Model):
    index = models.PositiveSmallIntegerField()
    student = models.ForeignKey(
        "users.Student", on_delete=models.PROTECT, null=True, blank=True
    )
    province = models.ForeignKey(Province, on_delete=models.PROTECT)


class SelectDefaultMajor(models.Model):
    index = models.PositiveSmallIntegerField()
    student = models.ForeignKey(
        "users.Student", on_delete=models.PROTECT, null=True, blank=True
    )
    major = models.ForeignKey(Major, on_delete=models.PROTECT)


class MajorSelection(models.Model):
    student = models.ForeignKey('users.Student', on_delete=models.PROTECT)
    booklet_row = models.ForeignKey(BookletRow, on_delete=models.PROTECT)
    head = models.BooleanField(default=False)
    # next_node = models.ForeignKey(MajorSelectionNode, on_delete=models.SET_NULL, blank=True, null=True)
    rank = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return '{} {} {}'.format(self.student.name, self.booklet_row.major.title, self.booklet_row.university.title)

    class Meta:
        # unique_together = ('booklet_row', 'student')
        verbose_name = _('major selection')
        verbose_name_plural = _('majors selection')

    def delete(self, *args, **kwargs):
        # Start a transaction to ensure atomicity
        with transaction.atomic():
            # Decrement the ranks of the subsequent MajorSelection objects
            MajorSelection.objects.filter(
                student=self.student,
                rank__gt=self.rank
            ).update(rank=models.F('rank') - 1)

            # Call the superclass delete method to delete the object
            super(MajorSelection, self).delete(*args, **kwargs)

    # booklet_row = models.ForeignKey(BookletRow, on_delete=models.PROTECT)
    # student = models.ForeignKey("users.Student", on_delete=models.PROTECT)
    # rank = models.PositiveSmallIntegerField(null=True, blank=True)

    # def __str__(self):
    #     return "{} {} {}".format(
    #         self.student.name,
    #         self.booklet_row.major.title,
    #         self.booklet_row.university.title,
    #     )

    # class Meta:
    #     unique_together = ("booklet_row", "student")
    #     verbose_name = _("major selection")
    #     verbose_name_plural = _("majors selection")


class MajorSelectionNode(models.Model):
    major_selection = models.ForeignKey(MajorSelection, on_delete=models.CASCADE, related_name='major_selection')
    next_major_selection = models.ForeignKey(MajorSelection, on_delete=models.CASCADE, null=True, blank=True, related_name='next_major_selection')

    def __str__(self):
        return self.major_selection.student.name

    class Meta:
        # unique_together = ('booklet_row', 'student')
        verbose_name = _('major selection node')
        verbose_name_plural = _('majors selection node')