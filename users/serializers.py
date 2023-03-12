from rest_framework import serializers
from rest_framework.authtoken.models import Token

from users.models import Student, Advisor


class StudentLoginSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField('get_token')
    gender = serializers.SerializerMethodField('get_gender')
    field_of_study = serializers.SerializerMethodField('get_field_of_study')
    province = serializers.SlugRelatedField(read_only=True, slug_field='title')

    # report_card = serializers.SerializerMethodField('get_report_card')

    def get_token(self, obj):
        Token.objects.filter(user=obj).delete()
        token = Token.objects.create(user=obj)
        return token.key

    def get_gender(self, obj):
        return obj.get_gender_display()

    def get_field_of_study(self, obj):
        return obj.get_field_of_study_display()

    # def get_report_card(self, obj):
    #     if ReportCard.objects.filter(student=obj):
    #         return True
    #     else:
    #         return False

    class Meta:
        model = Student
        fields = ['id', 'name', 'gender', 'national_code',
                  'field_of_study', 'province', 'token']


class AdvisorLoginSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField('get_token')

    def get_token(self, obj):
        Token.objects.filter(user=obj).delete()
        token = Token.objects.create(user=obj)
        return token.key

    class Meta:
        model = Advisor
        fields = ['id', 'name', 'token']


class StudentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'


class StudentRetrieveListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
