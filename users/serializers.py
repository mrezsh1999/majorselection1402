from rest_framework import serializers
from rest_framework.authtoken.models import Token

from users.models import Student, Advisor, ReportCard


class StudentLoginSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField("get_token")
    gender = serializers.SerializerMethodField("get_gender")
    field_of_study = serializers.SerializerMethodField("get_field_of_study")
    province = serializers.SlugRelatedField(read_only=True, slug_field="title")
    user_type = serializers.SerializerMethodField("get_user_type")

    def get_token(self, obj):
        Token.objects.filter(user=obj).delete()
        token = Token.objects.create(user=obj)
        return token.key

    def get_gender(self, obj):
        return obj.get_gender_display()

    def get_field_of_study(self, obj):
        return obj.get_field_of_study_display()

    def get_user_type(self, obj):
        return "student"

    class Meta:
        model = Student
        fields = [
            "id",
            "name",
            "gender",
            "national_code",
            "field_of_study",
            "province",
            "token",
            "user_type",
        ]


class AdvisorLoginSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField("get_token")
    user_type = serializers.SerializerMethodField("get_user_type")

    def get_token(self, obj):
        Token.objects.filter(user=obj).delete()
        token = Token.objects.create(user=obj)
        return token.key

    def get_user_type(self, obj):
        if obj.is_advisor:
            return "advisor"
        elif obj.is_manager:
            return "manager"

    class Meta:
        model = Advisor
        fields = ["id", "name", "token", "user_type"]


class StudentListSerializer(serializers.ModelSerializer):
    field_of_study = serializers.SerializerMethodField("get_field_of_study")
    province = serializers.SlugRelatedField(slug_field="title", read_only=True)
    gender = serializers.SerializerMethodField("get_gender")
    is_state_report_card = serializers.SerializerMethodField("get_is_state_report_card")

    def get_is_state_report_card(self, obj):
        try:
            ReportCard.objects.get(student=obj)
            return True
        except ReportCard.DoesNotExist:
            return False

    def get_field_of_study(self, obj):
        return obj.get_field_of_study_display()

    def get_gender(self, obj):
        return obj.get_gender_display()

    class Meta:
        model = Student
        fields = [
            "id",
            "name",
            "mobile",
            "national_code",
            "field_of_study",
            "province",
            "gender",
            "is_state_report_card",
            "is_state_choose_booklet_rows_done",
            "is_state_final_approval",
        ]


class StudentRetrieveListSerializer(serializers.ModelSerializer):
    gender = serializers.ChoiceField(choices=Student.GENDER)
    field_of_study = serializers.ChoiceField(choices=Student.FIELD_OF_STUDY)
    province = serializers.SlugRelatedField(slug_field="title", read_only=True)
    report_card = serializers.SerializerMethodField("get_report_card")

    def get_report_card(self, obj):
        if ReportCard.objects.filter(student=obj):
            request = self.context.get("request")
            return request.build_absolute_uri(
                ReportCard.objects.get(student=obj).report_card_file.url
            )

    class Meta:
        model = Student
        fields = [
            "id",
            "name",
            "gender",
            "national_code",
            "field_of_study",
            "volunteer_code",
            "province",
            "report_card",
            "is_state_choose_default",
            "is_state_choose_booklet_rows_done",
        ]


class ReportCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportCard
        fields = ["report_card_file"]
