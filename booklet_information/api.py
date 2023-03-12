from django_filters.rest_framework import DjangoFilterBackend, Filter, FilterSet
from rest_framework.decorators import action
from pyexcel_xlsx import get_data
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, filters, status

from booklet_information.models import BookletRow, SelectDefaultProvince, SelectDefaultMajor, SelectProvinceForMajor, \
    Major, Province, University, SelectProvince
from booklet_information.serializers import InfoSerializer, SelectDefaultProvinceListSerializer, \
    SelectProvinceForMajorCreateSerializer, MajorSerializer, ProvinceSerializer, MajorSelectionCreateSerializer, \
    SelectProvinceForMajorSerializer


class ListFilter(Filter):
    def filter(self, qs, value):
        if not value:
            return qs

        self.lookup_expr = 'in'
        values = value.split(',')
        return super(ListFilter, self).filter(qs, values)


class InfoFilter(FilterSet):
    major_ids = ListFilter(field_name='major_id')
    university_ids = ListFilter(field_name='university_id')
    university__province_ids = ListFilter(field_name='university__province_id')

    class Meta:
        model = BookletRow
        fields = ['major_ids', 'university_ids', 'university__province_ids', 'exam_based', 'course', 'gender',
                  'major__field_of_study']


# class StandardResultsSetPagination(PageNumberPagination):
#     page_size = 20
#     page_size_query_param = 'page_size'
#     max_page_size = 1000


class InfoViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  GenericViewSet):
    model = BookletRow
    queryset = BookletRow.objects.all()
    serializer_class = InfoSerializer
    # pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filter_class = InfoFilter
    search_fields = ['major_code', 'major__title',
                     'university__title', 'university__province__title']

    def create(self, request, *args, **kwargs):
        list10 = []
        excel_file = request.data.get('file')
        data = get_data(excel_file, column_limit=8)
        rows = data['Sheet1']
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

            if gender == ' ' or gender == '' or gender == None:
                g = 2
            elif gender == 1:
                g = 1
            elif gender == 2:
                g = 0

            if exam_based == 'با آزمون':
                exam_based = True
            elif exam_based == 'صرفا با سوابق تحصیلی':
                exam_based = False

            if course == 'روزانه':
                q = 0

            elif course == 'نوبت دوم':
                q = 1

            elif course == 'پردیس خودگردان':
                q = 2

            elif course == 'شهریه پرداز':
                q = 3

            elif course == 'پیام نور':
                q = 4

            elif course == 'غیر انتفاعی':
                q = 5

            elif course == 'مجازی':
                q = 6

            elif course == 'خودگردان آزاد':
                q = 7

            elif course == 'آزاد تمام وقت':
                q = 8

            elif course == 'فرهنگیان':
                q = 9

            elif course == 'بومی':
                q = 10

            if Major.objects.filter(title=major, field_of_study=0):
                y = Major.objects.get(title=major, field_of_study=0)
            else:
                y = Major.objects.create(title=major, field_of_study=0)

            if University.objects.filter(title=university):
                x = University.objects.filter(title=university).first()

            else:
                z = Province.objects.get(title=province)
                x = University.objects.create(
                    title=university, province=z)

            # Example.objects.update_or_create(exam_based=exam_based,
            #                                  course=q,
            #                                  university=x,
            #                                  gender=g,
            #                                  major=y,
            #                                  defaults={'code': code})
            BookletRow.objects.create(exam_based=exam_based,
                                      course=q,
                                      university=x,
                                      gender=g,
                                      major=y,
                                      major_code=code)
        return Response('ok')

    @action(detail=False, methods=['DELETE'])
    def delete(self, request):
        BookletRow.objects.all().delete()
        return Response('ok')

    @action(detail=False, methods=['POST', 'GET'])
    def booklet_rows_query(self, request):
        if request.method == "POST":
            all_rows = []
            pardis_rows = []
            major_index = 0
            province_index = 0
            SelectProvinceForMajor.objects.all().delete()
            for data in request.data:
                major_index += 1
                province_index = 0
                for province in data['select_province']:
                    province_index += 1
                    select_province = SelectProvince.objects.get_or_create(
                        index=province_index, province_id=province['province'])
                    select_provice_for_major = SelectProvinceForMajor.objects.get_or_create(
                        index=major_index, major_id=data['major'])
                    select_provice_for_major[0].select_province.add(
                        select_province[0])
                    daily_nightly_list = list(
                        BookletRow.objects.filter(major_id=data['major'], university__province_id=province['province'],
                                                  course__in=[0, 1]).order_by('course'))
                    all_rows += daily_nightly_list

                    pardis_list = list(
                        BookletRow.objects.filter(major_id=data['major'], university__province_id=province['province'],
                                                  course=2))
                    pardis_rows += pardis_list
                all_rows += pardis_rows

            serializer = MajorSelectionCreateSerializer(all_rows, many=True)
            return Response(serializer.data)

        elif request.method == "GET":
            all_rows = SelectProvinceForMajor.objects.all()
            serializer = SelectProvinceForMajorSerializer(all_rows, many=True)
            return Response(serializer.data)


class SelectDefaultProvinceViewSet(mixins.ListModelMixin,
                                   GenericViewSet):
    model = SelectDefaultProvince
    queryset = SelectDefaultProvince.objects.all()
    serializer_class = SelectDefaultProvinceListSerializer


class SelectProvinceForMajorViewSet(mixins.CreateModelMixin,
                                    GenericViewSet):
    model = SelectProvinceForMajor

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SelectProvinceForMajorCreateSerializer
        # elif self.request.method == 'GET':
        #     return SelectDefaultProvinceListSerializer

    def create(self, request, *args, **kwargs):
        # student filter
        if request.data:
            SelectDefaultMajor.objects.all().delete()
            SelectDefaultProvince.objects.all().delete()
            major_index = 0
            province_index = 0
            final_list = []
            x = dict()
            for major in request.data[0]:
                major_index += 1
                province_index = 0
                SelectDefaultMajor.objects.get_or_create(
                    index=major_index, major_id=major['major'])
                x = major
                select_province = []
                for province in request.data[1]:
                    province_index += 1
                    SelectDefaultProvince.objects.get_or_create(
                        index=province_index, province_id=province['province'])
                    select_province.append(province)
                    # print(select_province)
                    if province_index == len(request.data[1]):
                        x['select_province'] = select_province
                        final_list.append(x)

            # print(final_list)
            SelectProvinceForMajor.objects.all().delete()
            counter = 0
            for select_province_for_major in final_list:
                counter += 1
                select_province_for_major['index'] = counter

            serializer = self.get_serializer(data=final_list, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MajorViewSet(mixins.ListModelMixin,
                   GenericViewSet):
    model = Major
    queryset = Major.objects.all().order_by('title')
    serializer_class = MajorSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ['field_of_study']
    search_fields = ['title']


class ProvinceViewSet(mixins.ListModelMixin,
                      GenericViewSet):
    model = Province
    queryset = Province.objects.all().order_by('title')
    serializer_class = ProvinceSerializer
    search_fields = ['title']