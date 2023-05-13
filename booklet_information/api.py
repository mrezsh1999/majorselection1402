import os

from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend, Filter, FilterSet
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from pyexcel_xlsx import get_data
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, filters, status
from rest_framework.permissions import IsAuthenticated

from booklet_information.models import (
    BookletRow,
    SelectDefaultProvince,
    SelectDefaultMajor,
    SelectProvinceForMajor,
    Major,
    Province,
    University,
    SelectProvince,
    MajorSelection,
)
from booklet_information.serializers import (
    InfoSerializer,
    SelectDefaultProvinceListSerializer,
    SelectProvinceForMajorCreateSerializer,
    MajorSerializer,
    ProvinceSerializer,
    BookletRowsQueryCreateSerializer,
    BookletRowsQueryListSerializer,
    UniversityListSerializer,
    MajorSelectionListSerializer,
    MajorSelectionCreateSerializer,
    MajorSelectionDeleteSerializer,
    MajorSelectionResetSerializer,
)
from users.models import Student, User

from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Image
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas

from bidi.algorithm import get_display
from rtl import reshaper
import textwrap


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_student is True


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_manager is True


class IsAdvisor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_advisor is True


class ListFilter(Filter):
    def filter(self, qs, value):
        if not value:
            return qs

        self.lookup_expr = "in"
        values = value.split(",")
        return super(ListFilter, self).filter(qs, values)


class InfoFilter(FilterSet):
    major_ids = ListFilter(field_name="major_id")
    university_ids = ListFilter(field_name="university_id")
    university__province_ids = ListFilter(field_name="university__province_id")

    class Meta:
        model = BookletRow
        fields = [
            "major_ids",
            "university_ids",
            "university__province_ids",
            "exam_based",
            "course",
            "gender",
            "major__field_of_study",
        ]


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 1000


class InfoViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    model = BookletRow
    queryset = BookletRow.objects.all()
    serializer_class = InfoSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = InfoFilter
    search_fields = [
        "major_code",
        "major__title",
        "university__title",
        "university__province__title",
    ]

    def create(self, request, *args, **kwargs):
        list10 = []
        excel_file = request.data.get("file")
        data = get_data(excel_file, column_limit=8)
        rows = data["Sheet1"]
        rows.pop(0)

        for row in rows:
            y = x = q = g = None
            province = row[0]
            university = row[1]
            major = row[2]
            code = row[3]
            course = row[4]
            exam_based = row[5]
            try:
                gender = row[6]
            except:
                pass
            # rank = row[7]

            if gender == " " or gender == "" or gender == None:
                g = 2
            elif gender == 1:
                g = 1
            elif gender == 2:
                g = 0

            if exam_based == "با آزمون":
                exam_based = True
            elif exam_based == "صرفا با سوابق تحصیلی":
                exam_based = False

            if course == "روزانه":
                q = 0

            elif course == "نوبت دوم":
                q = 1

            elif course == "پردیس خودگردان":
                q = 2

            elif course == "شهریه پرداز":
                q = 3

            elif course == "پیام نور":
                q = 4

            elif course == "غیر انتفاعی":
                q = 5

            elif course == "مجازی":
                q = 6

            elif course == "خودگردان آزاد":
                q = 7

            elif course == "آزاد تمام وقت":
                q = 8

            elif course == "فرهنگیان":
                q = 9

            elif course == "بومی":
                q = 10

            if Major.objects.filter(title=major, field_of_study=0):
                y = Major.objects.get(title=major, field_of_study=0)
            else:
                y = Major.objects.create(title=major, field_of_study=0)

            if University.objects.filter(title=university):
                x = University.objects.filter(title=university).first()

            else:
                z = Province.objects.get(title=province)
                x = University.objects.create(title=university, province=z)

            # Example.objects.update_or_create(exam_based=exam_based,
            #                                  course=q,
            #                                  university=x,
            #                                  gender=g,
            #                                  major=y,
            #                                  defaults={'code': code})
            BookletRow.objects.create(
                exam_based=exam_based,
                course=q,
                university=x,
                gender=g,
                major=y,
                major_code=code,
            )
        return Response("ok")

    @action(detail=False, methods=["DELETE"])
    def delete(self, request):
        BookletRow.objects.all().delete()
        return Response("ok")

    @action(detail=False, methods=["POST", "GET"])
    def booklet_rows_query(self, request):
        student_id = request.GET.get("student_id")
        if request.method == "POST":
            all_rows = []
            major_index = 0
            SelectProvinceForMajor.objects.filter(student_id=student_id).delete()
            for data in request.data:
                major_index += 1
                province_index = 0
                for province in data["select_province"]:
                    province_index += 1
                    select_province = SelectProvince.objects.get_or_create(
                        index=province_index, province_id=province["province"]
                    )
                    select_province_for_major = (
                        SelectProvinceForMajor.objects.get_or_create(
                            major_id=data["major"],
                            student_id=student_id,
                            defaults={"index": major_index},
                        )
                    )
                    select_province_for_major[0].select_province.add(select_province[0])
                    daily_nightly_list = list(
                        BookletRow.objects.filter(
                            major_id=data["major"],
                            university__province_id=province["province"],
                        )
                    )
                    all_rows += daily_nightly_list

            student = Student.objects.get(id=student_id)
            student.is_state_choose_booklet_rows = True
            student.save()
            sorted_list = sorted(all_rows, key=lambda x: x.course)
            serializer = BookletRowsQueryCreateSerializer(sorted_list, many=True)
            return Response(serializer.data)

        elif request.method == "GET":
            all_rows = SelectProvinceForMajor.objects.filter(student_id=student_id)
            serializer = BookletRowsQueryListSerializer(all_rows, many=True)
            return Response(serializer.data)


class SelectDefaultProvinceViewSet(mixins.ListModelMixin, GenericViewSet):
    model = SelectDefaultProvince
    # queryset = SelectDefaultProvince.objects.all()
    serializer_class = SelectDefaultProvinceListSerializer

    def get_queryset(self):
        student_id = self.request.GET.get("student_id")
        return SelectDefaultProvince.objects.filter(student_id=student_id)


class SelectProvinceForMajorViewSet(mixins.CreateModelMixin, GenericViewSet):
    model = SelectProvinceForMajor

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SelectProvinceForMajorCreateSerializer

    def create(self, request, *args, **kwargs):
        student_id = request.GET.get("student_id")
        if request.data:
            SelectDefaultMajor.objects.filter(student_id=student_id).delete()
            SelectDefaultProvince.objects.filter(student_id=student_id).delete()
            major_index = 0
            final_list = []
            for major in request.data[0]:
                major_index += 1
                province_index = 0
                SelectDefaultMajor.objects.get_or_create(
                    index=major_index, major_id=major["major"], student_id=student_id
                )
                x = major
                select_province = []
                for province in request.data[1]:
                    province_index += 1
                    SelectDefaultProvince.objects.get_or_create(
                        index=province_index,
                        province_id=province["province"],
                        student_id=student_id,
                    )
                    select_province.append(province)
                    if province_index == len(request.data[1]):
                        x["select_province"] = select_province
                        x["student"] = student_id
                        final_list.append(x)

            SelectProvinceForMajor.objects.filter(student_id=student_id).delete()
            counter = 0
            for select_province_for_major in final_list:
                counter += 1
                select_province_for_major["index"] = counter

            serializer = self.get_serializer(data=final_list, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )


class MajorViewSet(mixins.ListModelMixin, GenericViewSet):
    model = Major
    queryset = Major.objects.all().order_by("title")
    serializer_class = MajorSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ["field_of_study"]
    search_fields = ["title"]


class ProvinceViewSet(mixins.ListModelMixin, GenericViewSet):
    model = Province
    queryset = Province.objects.all().order_by("title")
    serializer_class = ProvinceSerializer
    search_fields = ["title"]


class UniversityViewSet(mixins.ListModelMixin, GenericViewSet):
    model = University
    queryset = University.objects.all()
    permission_class = [IsAuthenticated]
    serializer_class = UniversityListSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    # filterset_fields = ['province', 'example__major__field_of_study']
    search_fields = ["title", "province__title"]


class MajorSelectionViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    model = MajorSelection

    def get_serializer_class(self):
        if self.request.method == "POST":
            return MajorSelectionCreateSerializer
        elif self.request.method == "GET":
            return MajorSelectionListSerializer
        elif self.request.method == "DELETE":
            return MajorSelectionDeleteSerializer

    def get_queryset(self):
        student_id = self.request.GET.get("student_id")
        return MajorSelection.objects.filter(student_id=student_id).order_by("rank")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            many=True,
            context={"student_id": request.GET.get("student_id")},
        )
        if serializer.is_valid():
            MajorSelection.objects.filter(
                student_id=request.GET.get("student_id")
            ).delete()
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            student = Student.objects.get(id=request.GET.get("student_id"))
            student.is_state_choose_booklet_rows_done = True
            student.save()
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = MajorSelection.objects.filter(id__in=kwargs["pk"].split(","))
        student = MajorSelection.objects.get(id=kwargs["pk"].split(",")[0]).student
        self.perform_destroy(instance)
        ranks = MajorSelection.objects.filter(student=student).order_by("rank")
        y = 0
        for rank in ranks:
            y += 1
            serializer = self.get_serializer(rank, data={"rank": y}, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["GET"])
    def reset_major_selection(self, request):
        student_id = request.GET.get("student_id")
        select_province_for_majors = SelectProvinceForMajor.objects.filter(
            student_id=student_id
        ).order_by("index")
        booklet_rows = []
        for select_province_for_major in select_province_for_majors:
            major_id = select_province_for_major.major_id
            select_province = select_province_for_major.select_province
            for province in select_province.order_by("index"):
                province_id = province.province.id
                booklet_row = BookletRow.objects.filter(
                    major_id=major_id, university__province_id=province_id
                )
                booklet_rows += booklet_row
        sorted_list = sorted(booklet_rows, key=lambda x: x.course)
        serializer = MajorSelectionResetSerializer(
            sorted_list, many=True, context={"student_id": student_id}
        )
        return Response(serializer.data)

    @action(detail=False, methods=["GET"])
    def pdf(self, request):
        def get_farsi_text(text):
            if reshaper.has_arabic_letters(text):
                words = text.split()
                reshaped_words = []
                for word in words:
                    if reshaper.has_arabic_letters(word):
                        # for reshaping and concating words
                        reshaped_text = reshaper.reshape(word)
                        # for right to left
                        bidi_text = get_display(reshaped_text)
                        reshaped_words.append(bidi_text)
                    else:
                        reshaped_words.append(word)
                reshaped_words.reverse()
                return " ".join(reshaped_words)
            return text
            # return bidi_text
            # return text

        class FooterCanvas(canvas.Canvas):
            def __init__(self, *args, **kwargs):
                canvas.Canvas.__init__(self, *args, **kwargs)
                self.pages = []
                self.width, self.height = LETTER

            def showPage(self):
                self.pages.append(dict(self.__dict__))
                self._startPage()

            def save(self):
                page_count = len(self.pages)
                for page in self.pages:
                    self.__dict__.update(page)
                    if self._pageNumber < 2:
                        self.draw_canvas(page_count)
                    else:
                        self.draw_canvas_second(page_count)
                    canvas.Canvas.showPage(self)
                canvas.Canvas.save(self)

            def draw_canvas(self, page_count):
                page = "Page %s of %s" % (self._pageNumber, page_count)
                x = 128
                self.saveState()
                self.setStrokeColorRGB(0, 0, 0)
                self.setLineWidth(0.5)
                self.drawImage(
                    os.getcwd() + "/" + "Logo.png",
                    self.width - inch * 2.5,
                    self.height - 70,
                    width=200,
                    height=50,
                    preserveAspectRatio=True,
                    mask="auto",
                )

                self.drawImage(
                    os.getcwd() + "/" + "check.png",
                    self.width - inch * 9,
                    self.height - 70,
                    width=200,
                    height=50,
                    preserveAspectRatio=True,
                    mask="auto",
                )

                self.line(30, 720, LETTER[0] - 50, 720)
                self.line(30, 78, LETTER[0] - 50, 78)
                self.setFont("Times-Roman", 10)
                self.drawString(LETTER[0] - x, 65, page)
                self.restoreState()

            def draw_canvas_second(self, page_count):
                page = "Page %s of %s" % (self._pageNumber, page_count)
                x = 128
                self.saveState()
                self.setStrokeColorRGB(0, 0, 0)
                self.setLineWidth(0.5)
                self.line(30, 78, LETTER[0] - 50, 78)
                self.setFont("Times-Roman", 10)
                self.drawString(LETTER[0] - x, 65, page)
                self.restoreState()

        global response
        os.chdir(
            r"C:/Users/Asus/Desktop/MajorFinal/majorselection1402/booklet_information/persian"
        )
        pdfmetrics.registerFont(TTFont("Persian", "Bahij-Nazanin-Regular.ttf"))

        styles = getSampleStyleSheet()
        stylesHeader = getSampleStyleSheet()
        stylesInstitue = getSampleStyleSheet()
        stylesName = getSampleStyleSheet()

        styles.add(
            ParagraphStyle(
                name="Right",
                alignment=TA_CENTER,
                fontName="Persian",
                fontSize=10,
            )
        )

        stylesHeader.add(
            ParagraphStyle(
                name="Right",
                alignment=TA_CENTER,
                fontName="Persian",
                fontSize=10,
                textColor=colors.white,
            )
        )

        stylesInstitue.add(
            ParagraphStyle(
                name="Right",
                alignment=TA_CENTER,
                fontName="Persian",
                fontSize=20,
                borderWidth=2,
                borderColor=colors.HexColor("#F9B33D"),
                borderRadius=15,
                textColor=colors.black,
                leftIndent=140,
                rightIndent=140,
            )
        )

        stylesName.add(
            ParagraphStyle(
                name="Right",
                alignment=TA_CENTER,
                fontName="Persian",
                fontSize=15,
                textColor=colors.black,
            )
        )

        def get_farsi_bulleted_text(text, wrap_length=None):
            farsi_text = get_farsi_text(text)
            if wrap_length:
                line_list = textwrap.wrap(farsi_text, wrap_length)
                line_list.reverse()
                # line_list[0] = '{} &#x02022;'.format(line_list[0])
                farsi_text = "<br/>".join(line_list)
                return "<font>%s</font>" % farsi_text
            return "<font>%s &#x02022;</font>" % farsi_text

        data = []
        student_id = None
        if request.user.is_advisor or request.user.is_manager:
            student_id = request.GET.get("student_id")
        elif request.user.is_student:
            student_id = request.user.id

        major_selections = (
            MajorSelection.objects.filter(student_id=student_id)
            .order_by("rank")
            .values_list(
                "booklet_row__major_code",
                "booklet_row__university__province__title",
                "booklet_row__exam_based",
                "booklet_row__course",
                "booklet_row__university__title",
                "booklet_row__major__title",
            )
        )
        q = 1
        for major_selection in major_selections:
            x = list(major_selection)
            x.insert(6, q)
            q += 1
            data.append(x)

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=tavana_pdf.pdf"

        elements = []
        x = get_farsi_bulleted_text("کد رشته", 40)
        p = Paragraph(x, stylesHeader["Right"])
        list_column_head = [
            p,
            "نام استان",
            "نحوه پذیرش",
            "دوره تحصیلی",
            "نام دانشگاه",
            "عنوان رشته",
            " ",
        ]
        data.insert(0, list_column_head)
        for i in range(len(data)):
            for j in range(1, 6):
                if j == 3:
                    if data[i][j] == 0:
                        data[i][j] = "روزانه"
                    elif data[i][j] == 1:
                        data[i][j] = "نوبت دوم"
                    elif data[i][j] == 2:
                        data[i][j] = "پردیس خودگردان"
                    elif data[i][j] == 3:
                        data[i][j] = "شهریه پرداز"
                    elif data[i][j] == 4:
                        data[i][j] = "پیام نور"
                    elif data[i][j] == 5:
                        data[i][j] = "غیرانتفاعی"
                    elif data[i][j] == 6:
                        data[i][j] = "مجازی"
                    elif data[i][j] == 7:
                        data[i][j] = "خودگردان آزاد"
                    elif data[i][j] == 8:
                        data[i][j] = "آزاد تمام وقت"
                    elif data[i][j] == 9:
                        data[i][j] = "فرهنگیان"
                    elif data[i][j] == 10:
                        data[i][j] = "بومی"

                elif j == 2:
                    if data[i][j]:
                        data[i][j] = "با آزمون"
                    elif not data[i][j]:
                        data[i][j] = "بدون آزمون"

                x = get_farsi_bulleted_text(data[i][j], 30)
                if i == 0:
                    p = Paragraph(x, stylesHeader["Right"])
                else:
                    p = Paragraph(x, styles["Right"])

                data[i][j] = p

        institue_text = "مجموعه آموزشی توانا"

        student_name = Student.objects.get(id=request.GET.get("student_id")).name

        student_name = (
            "نام دانش آموز: "
            + Student.objects.get(id=request.GET.get("student_id")).name
            + " / "
            + "نام مشاور: "
            + Student.objects.get(id=request.GET.get("student_id")).student_advisor.name
        )

        institue_text = get_farsi_text(institue_text) + "\n\n\n"
        student_name_text = "\n\n" + get_farsi_text(student_name) + "\n\n\n"

        doc = SimpleDocTemplate(
            response,
            title=Student.objects.get(id=request.GET.get("student_id")).name,
        )
        table = Table(data, colWidths=[50, 85, 60, 80, 150, 120, 20])

        table_style = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#6336F0")),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("VALIGN", (0, 0), (0, -1), "MIDDLE"),
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
            ("VALIGN", (1, 0), (1, -1), "MIDDLE"),
            ("ALIGN", (2, 0), (2, -1), "CENTER"),
            ("VALIGN", (2, 0), (2, -1), "MIDDLE"),
            ("ALIGN", (3, 0), (3, -1), "CENTER"),
            ("VALIGN", (3, 0), (3, -1), "MIDDLE"),
            ("ALIGN", (4, 0), (4, -1), "CENTER"),
            ("VALIGN", (4, 0), (4, -1), "MIDDLE"),
            ("ALIGN", (5, 0), (5, -1), "CENTER"),
            ("VALIGN", (5, 0), (5, -1), "MIDDLE"),
            ("ALIGN", (6, 0), (6, -1), "CENTER"),
            ("VALIGN", (6, 0), (6, -1), "MIDDLE"),
            ("BOX", (0, 0), (-1, 0), 2, colors.black),
            ("INNERGRID", (0, 0), (-1, -1), 0.75, colors.black),
            ("BOX", (0, 0), (-1, -1), 0.75, colors.black),
        ]

        for i, row in enumerate(data):
            if i == 0:
                table_style.append(
                    ("BACKGROUND", (0, i), (-1, i), colors.HexColor("#6336F0")),
                )
            else:
                if i % 2 == 0:
                    table_style.append(
                        ("BACKGROUND", (0, i), (-1, i), colors.HexColor("#CCCCFF")),
                    )
                else:
                    table_style.append(
                        ("BACKGROUND", (0, i), (-1, i), colors.HexColor("#E6E6FA")),
                    )

        table.setStyle(table_style)

        os.chdir(
            r"C:/Users/Asus/Desktop/MajorFinal/majorselection1402/booklet_information/images"
        )
        logo_url = "Logo.png"
        elements.append(table)
        doc.multiBuild(
            [
                Paragraph(
                    institue_text.replace("\n", "<br />"),
                    stylesInstitue["Right"],
                ),
            ]
            + [
                Paragraph(
                    student_name_text.replace("\n", "<br />"),
                    stylesName["Right"],
                ),
            ]
            + elements,
            canvasmaker=FooterCanvas,
        )
        # doc.build(

        # )
        return response
