from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from booklet_information.models import BookletRow, SelectDefaultProvince, SelectDefaultMajor, SelectProvinceForMajor, \
    SelectProvince, Province, Major


class InfoSerializer(serializers.ModelSerializer):
    university = serializers.SerializerMethodField('get_university')
    major = serializers.SerializerMethodField('get_major')
    course = serializers.SerializerMethodField('get_course')
    exam_based = serializers.SerializerMethodField('get_exam_based')
    gender = serializers.SerializerMethodField('get_gender')
    province = serializers.SerializerMethodField('get_province')
    field_of_study = serializers.SerializerMethodField('get_field_of_study')

    def get_university(self, obj):
        return obj.university.title

    def get_major(self, obj):
        return obj.major.title

    def get_course(self, obj):
        return obj.get_course_display()

    def get_exam_based(self, obj):
        if obj.exam_based:
            return 'با آزمون'
        return 'صرفا با سوابق تحصیلی'

    def get_gender(self, obj):
        return obj.get_gender_display()

    def get_province(self, obj):
        return obj.university.province.name

    def get_field_of_study(self, obj):
        return obj.major.get_field_of_study_display()

    class Meta:
        model = BookletRow
        fields = ['id', 'university', 'major', 'course', 'exam_based', 'major_code', 'gender', 'province',
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
            print(select_province[0])
            y[0].select_province.add(select_province[0])
            x.append(select_province[0])
        validated_data['select_province'] = x
        return validated_data

    class Meta:
        model = SelectProvinceForMajor
        fields = ['index', 'major', 'select_province']

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


class MajorSelectionCreateSerializer(serializers.ModelSerializer):
    university = serializers.SlugRelatedField(
        slug_field='title', read_only=True)
    major_title = serializers.SerializerMethodField('get_major_title')

    def get_major_title(self, obj):
        return obj.major.title

    class Meta:
        model = BookletRow
        fields = ['id', 'major_code', 'exam_based', 'course',
                  'gender', 'university', 'major', 'major_title']


class SelectProvinceManyToManySerializer(serializers.ModelSerializer):
    province_title = serializers.SerializerMethodField('get_province_title')

    def get_province_title(self, obj):
        print(obj)
        return obj.province.title

    class Meta:
        model = SelectProvince
        fields = ['province', 'province_title']


class SelectProvinceForMajorSerializer(serializers.ModelSerializer):
    major_title = serializers.SerializerMethodField('get_major_title')
    select_province = SelectProvinceManyToManySerializer(many=True)

    def get_major_title(self, obj):
        return obj.major.title

    class Meta:
        model = SelectProvinceForMajor
        fields = ['major', 'major_title', 'select_province']