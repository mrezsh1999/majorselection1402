from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueTogetherValidator

from booklet_information.models import BookletRow, SelectDefaultProvince, SelectDefaultMajor, SelectProvinceForMajor, \
    SelectProvince, Province, Major, University, MajorSelection
from users.models import Student


class InfoSerializer(serializers.ModelSerializer):
    university = serializers.SlugRelatedField(slug_field='title', read_only=True)
    major_title = serializers.SerializerMethodField('get_major_title')
    course = serializers.SerializerMethodField('get_course')
    exam_based = serializers.SerializerMethodField('get_exam_based')
    gender = serializers.SerializerMethodField('get_gender')
    province = serializers.SerializerMethodField('get_province')
    field_of_study = serializers.SerializerMethodField('get_field_of_study')

    def get_university(self, obj):
        return obj.university.title

    def get_major_title(self, obj):
        return obj.major.title

    def get_course(self, obj):
        return obj.get_course_display()

    def get_exam_based(self, obj):
        return obj.get_exam_based_display()

    def get_gender(self, obj):
        return obj.get_gender_display()

    def get_province(self, obj):
        return obj.university.province.title

    def get_field_of_study(self, obj):
        return obj.major.get_field_of_study_display()

    class Meta:
        model = BookletRow
        fields = ['id', 'province', 'university', 'major_title', 'major', 'major_code', 'course', 'exam_based',
                  'gender',
                  'field_of_study']


class SelectDefaultProvinceListSerializer(serializers.ModelSerializer):
    province_title = serializers.SerializerMethodField('get_province_title')

    def get_province_title(self, obj):
        return obj.province.title

    class Meta:
        model = SelectDefaultProvince
        fields = ['id', 'index', 'province', 'province_title']


class SelectProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelectProvince
        fields = ['index', 'province']


class SelectProvinceForMajorCreateSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        x = []
        counter = 0
        list_select_province = validated_data.pop('select_province')
        for instance in list_select_province:
            counter += 1
            province = get_object_or_404(Province, pk=instance['province'])
            select_province = SelectProvince.objects.get_or_create(
                province=province, index=counter)
            y = SelectProvinceForMajor.objects.get_or_create(**validated_data)
            y[0].select_province.add(select_province[0])
            x.append(select_province[0])
        validated_data['select_province'] = x
        student = Student.objects.get(id=self.context.get('request').GET.get('student_id'))
        student.is_state_choose_default = True
        student.save()
        return validated_data

    class Meta:
        model = SelectProvinceForMajor
        fields = ['index', 'major', 'select_province', 'student']

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        x = instance['select_province']
        repr['select_province'] = SelectProvinceSerializer(x, many=True).data
        return repr

    def get_fields(self):
        fields = super().get_fields()
        if self.context['request'].method in ['POST']:
            fields['select_province'] = serializers.ListField(
                write_only=True,
            )
        return fields


class MajorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Major
        fields = ['id', 'title']


class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ['id', 'title']


class BookletRowsQueryCreateSerializer(serializers.ModelSerializer):
    university = serializers.SlugRelatedField(
        slug_field='title', read_only=True)
    province = serializers.SerializerMethodField('get_province')
    major_title = serializers.SerializerMethodField('get_major_title')
    course = serializers.SerializerMethodField('get_major_course')
    exam_based = serializers.SerializerMethodField('get_exam_based')
    gender = serializers.SerializerMethodField('get_gender')
    field_of_study = serializers.SerializerMethodField('get_field_of_study')

    def get_province(self, obj):
        return obj.university.province.title

    def get_major_title(self, obj):
        return obj.major.title

    def get_major_course(self, obj):
        return obj.get_course_display()

    def get_exam_based(self, obj):
        return obj.get_exam_based_display()

    def get_gender(self, obj):
        return obj.get_gender_display()

    def get_field_of_study(self, obj):
        return obj.major.get_field_of_study_display()

    class Meta:
        model = BookletRow
        fields = ['id', 'province', 'university', 'major_title', 'major', 'major_code', 'course', 'exam_based',
                  'gender', 'field_of_study']


class SelectProvinceManyToManySerializer(serializers.ModelSerializer):
    province_title = serializers.SerializerMethodField('get_province_title')

    def get_province_title(self, obj):
        print(obj)
        return obj.province.title

    class Meta:
        model = SelectProvince
        fields = ['province', 'province_title']


class BookletRowsQueryListSerializer(serializers.ModelSerializer):
    major_title = serializers.SerializerMethodField('get_major_title')
    select_province = SelectProvinceManyToManySerializer(many=True)

    def get_major_title(self, obj):
        return obj.major.title

    class Meta:
        model = SelectProvinceForMajor
        fields = ['major', 'major_title', 'select_province']


class UniversityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ['id', 'title']


class MajorSelectionListSerializer(serializers.ModelSerializer):
    university = serializers.SerializerMethodField('get_university')
    province = serializers.SerializerMethodField('get_province')
    major_title = serializers.SerializerMethodField('get_major_title')
    course = serializers.SerializerMethodField('get_major_course')
    exam_based = serializers.SerializerMethodField('get_exam_based')
    gender = serializers.SerializerMethodField('get_gender')
    field_of_study = serializers.SerializerMethodField('get_field_of_study')
    major = serializers.SerializerMethodField('get_major')
    major_code = serializers.SerializerMethodField('get_major_code')

    def get_major_code(self, obj):
        return obj.booklet_row.major_code

    def get_major(self, obj):
        return obj.booklet_row.major.id

    def get_university(self, obj):
        return obj.booklet_row.university.title

    def get_province(self, obj):
        return obj.booklet_row.university.province.title

    def get_major_title(self, obj):
        return obj.booklet_row.major.title

    def get_major_course(self, obj):
        return obj.booklet_row.get_course_display()

    def get_exam_based(self, obj):
        return obj.booklet_row.get_exam_based_display()

    def get_gender(self, obj):
        return obj.booklet_row.get_gender_display()

    def get_field_of_study(self, obj):
        return obj.booklet_row.major.get_field_of_study_display()

    class Meta:
        model = MajorSelection
        fields = ['id', 'rank', 'province', 'university', 'major_title', 'major', 'major_code', 'course', 'exam_based',
                  'gender', 'field_of_study']


class HumanListSerializer(serializers.ListSerializer):

    def validate(self, data):
        validation_set = set()

        for item in data:
            if item['booklet_row'] in validation_set:
                raise serializers.ValidationError('!رشته [{}] تکراری است'.format(item['booklet_row']))
            else:
                validation_set.add(item['booklet_row'])

        return data


class MajorSelectionCreateSerializer(serializers.ModelSerializer):
    rank = 0

    def create(self, validated_data):
        self.rank += 1
        obj = MajorSelection.objects.create(**validated_data, rank=self.rank,
                                            student_id=self.context.get('student_id'))
        obj.save()
        return obj

    class Meta:
        model = MajorSelection
        fields = ['id', 'booklet_row']
        list_serializer_class = HumanListSerializer


class MajorSelectionDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MajorSelection
        fields = ['rank', 'student', 'booklet_row']


class MajorSelectionResetSerializer(serializers.ModelSerializer):
    university = serializers.SlugRelatedField(
        slug_field='title', read_only=True)
    province = serializers.SerializerMethodField('get_province')
    major_title = serializers.SerializerMethodField('get_major_title')
    course = serializers.SerializerMethodField('get_major_course')
    exam_based = serializers.SerializerMethodField('get_exam_based')
    gender = serializers.SerializerMethodField('get_gender')
    field_of_study = serializers.SerializerMethodField('get_field_of_study')
    rank = serializers.SerializerMethodField('get_rank')

    def get_province(self, obj):
        return obj.university.province.title

    def get_major_title(self, obj):
        return obj.major.title

    def get_major_course(self, obj):
        return obj.get_course_display()

    def get_exam_based(self, obj):
        return obj.get_exam_based_display()

    def get_gender(self, obj):
        return obj.get_gender_display()

    def get_field_of_study(self, obj):
        return obj.major.get_field_of_study_display()

    def get_rank(self, obj):
        if (obj.id,) in MajorSelection.objects.filter(student_id=self.context.get('student_id')).values_list('booklet_row_id'):
            return MajorSelection.objects.get(booklet_row=obj).rank

    class Meta:
        model = BookletRow
        fields = ['id', 'province', 'university', 'major_title', 'major', 'major_code', 'course', 'exam_based',
                  'gender', 'field_of_study', 'rank']
