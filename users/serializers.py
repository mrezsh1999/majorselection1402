from rest_framework import serializers
from rest_framework.authtoken.models import Token

from users.models import Student, Advisor, ReportCard, Manager
import jdatetime

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
        # Check if a token already exists for the user
        existing_token = Token.objects.filter(user=obj).first()

        if existing_token:
            # If a token exists, return the existing token key without deleting it
            return existing_token.key
        else:
            # If there is no token for the user, create a new one
            token = Token.objects.create(user=obj)
            return token.key
        
    # def get_token(self, obj):
    #     Token.objects.filter(user=obj).delete()
    #     token = Token.objects.create(user=obj)
    #     return token.key

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

class StudentListSerializerAdvisor(serializers.ModelSerializer):
    field_of_study = serializers.SerializerMethodField("get_field_of_study")
    province = serializers.SlugRelatedField(slug_field="title", read_only=True)
    gender = serializers.SerializerMethodField("get_gender")
    is_state_report_card = serializers.SerializerMethodField("get_is_state_report_card")
    is_state_choose_booklet_rows_done = serializers.SerializerMethodField("get_is_state_choose_booklet_rows_done")
    is_state_final_approval = serializers.SerializerMethodField("get_is_state_final_approval")

    def get_is_state_choose_booklet_rows_done(self, obj):
        return "انجام شده" if obj.is_state_choose_booklet_rows_done else "انجام نشده"

    def get_is_state_final_approval(self, obj):
        return "تایید شده" if obj.is_state_final_approval else "تایید نشده"
    
    def get_is_state_report_card(self, obj):
        try:
            ReportCard.objects.get(student=obj)
            return "وجود دارد"
        except ReportCard.DoesNotExist:
            return "وجود ندارد"

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

class StudentListSerializerManager(serializers.ModelSerializer):
    field_of_study = serializers.SerializerMethodField("get_field_of_study")
    province = serializers.SlugRelatedField(slug_field="title", read_only=True)
    gender = serializers.SerializerMethodField("get_gender")
    is_state_report_card = serializers.SerializerMethodField("get_is_state_report_card")
    is_state_choose_booklet_rows_done = serializers.SerializerMethodField("get_is_state_choose_booklet_rows_done")
    is_state_final_approval = serializers.SerializerMethodField("get_is_state_final_approval")
    advisor_name = serializers.SerializerMethodField("get_advisor_name")

    def get_is_state_choose_booklet_rows_done(self, obj):
        return "انجام شده" if obj.is_state_choose_booklet_rows_done else "انجام نشده"

    def get_is_state_final_approval(self, obj):
        return "تایید شده" if obj.is_state_final_approval else "تایید نشده"
    
    def get_is_state_report_card(self, obj):
        try:
            ReportCard.objects.get(student=obj)
            return "وجود دارد"
        except ReportCard.DoesNotExist:
            return "وجود ندارد"

    def get_field_of_study(self, obj):
        return obj.get_field_of_study_display()

    def get_gender(self, obj):
        return obj.get_gender_display()

    def get_advisor_name(self, obj):
        return obj.student_advisor.name

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
            "advisor_name"
        ]

class StudentListSerializerManagerNew(serializers.ModelSerializer):
    field_of_study = serializers.SerializerMethodField("get_field_of_study")
    is_state_final_approval = serializers.SerializerMethodField("get_is_state_final_approval")
    advisor_name = serializers.SerializerMethodField("get_advisor_name")
    process_info = serializers.SerializerMethodField("get_process_info")

    def get_is_state_final_approval(self, obj):
        return "تایید شده" if obj.is_state_final_approval else "تایید نشده"

    def get_field_of_study(self, obj):
        return obj.get_field_of_study_display()

    def get_advisor_name(self, obj):
        if obj.student_advisor:
            return obj.student_advisor.name
        return 'ندارد'
    

    def get_process_info(self, obj):
        if obj.process_start_time and obj.process_end_time:
            duration = obj.process_end_time - obj.process_start_time
            hours = duration.seconds // 3600
            minutes = (duration.seconds // 60) % 60
            duration_str = f"{hours}:{minutes}"
            start_time = obj.process_start_time.strftime('%H:%M')
            start_jalali = jdatetime.datetime.fromgregorian(datetime=obj.process_start_time)
            start_date_str = start_jalali.strftime('%m/%d')  # Month and day only
            return f"{start_time}\t{start_date_str}"  # Combined string with tab space
        return "انجام نشده"
    

    class Meta:
        model = Student
        fields = [
            "id",
            "name",
            "field_of_study",
            "is_state_final_approval",
            "advisor_name",
            "process_info"
        ]


class StudentRetrieveListSerializer(serializers.ModelSerializer):
    gender = serializers.SerializerMethodField()
    field_of_study = serializers.SerializerMethodField()
    field_of_study_id = serializers.SerializerMethodField()
    province = serializers.SlugRelatedField(slug_field="title", read_only=True)
    province_id = serializers.SerializerMethodField()
    advisor_name = serializers.SerializerMethodField()
    advisor_id = serializers.SerializerMethodField()
    report_card = serializers.SerializerMethodField("get_report_card")

    def get_field_of_study_id(self, obj):
        return obj.field_of_study
    
    def get_province_id(self, obj):
        return obj.province.id
    
    def get_advisor_id(self, obj):
        return obj.student_advisor.id if obj.student_advisor else None
    
    def get_gender(self, obj):
        return obj.get_gender_display()

    def get_field_of_study(self, obj):
        return obj.get_field_of_study_display()
    
    def get_advisor_name(self, obj):
        return obj.student_advisor.name if obj.student_advisor else None

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
            "first_name",
            "last_name",
            "province_id",
            "advisor_id",
            "field_of_study_id",
            "gender",
            "national_code",
            "field_of_study",
            "volunteer_code",
            "province",
            "report_card",
            "is_state_choose_default",
            "is_state_choose_booklet_rows_done",
            "is_state_final_approval",
            "advisor_name",
            "mobile"
        ]


class ReportCardSerializer(serializers.ModelSerializer):
    report_card_file = serializers.FileField(required=False, allow_null=True)
    class Meta:
        model = ReportCard
        fields = ["report_card_file"]

class StudentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'mobile', 'gender', 'province', 'field_of_study', 'is_student', 'school']

from rest_framework import serializers
from .models import Student, Advisor, School, Province

class StudentUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    mobile = serializers.CharField(max_length=11, required=False)
    gender = serializers.ChoiceField(choices=Student.GENDER, required=False)
    national_code = serializers.CharField(max_length=10, required=False, allow_blank=True, allow_null=True)
    field_of_study = serializers.ChoiceField(choices=Student.FIELD_OF_STUDY, required=False)
    province = serializers.PrimaryKeyRelatedField(queryset=Province.objects.all(), required=False)
    student_advisor = serializers.PrimaryKeyRelatedField(queryset=Advisor.objects.all(), required=False)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        return instance

class AdvisorUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advisor
        fields = ['first_name', 'last_name', 'mobile', 'is_advisor', 'manager_field']

class StudentCreationSerializer(serializers.ModelSerializer):
    report_card = ReportCardSerializer(required=False, allow_null=True)
    
    # Add is_student to serializer fields
    is_student = serializers.BooleanField(default=True, read_only=True)

    class Meta:
        model = Student
        fields = [
            'first_name', 'last_name', 'mobile', 'gender',
            'field_of_study', 'province', 'student_advisor',
            'report_card', 'is_student'
        ]

    def create(self, validated_data):
        report_card_data = validated_data.pop('report_card', None)
        
        # Ensure is_student is always True
        validated_data['is_student'] = True
        
        # Get the manager and school from the request context
        manager = Manager.objects.get(id=self.context['request'].user.id)
        school = manager.school_set.first()
        
        # Set the school for the student if available
        if school:
            validated_data['school'] = school
        else:
            raise serializers.ValidationError({'school': 'Manager does not have an associated school'})
        
        student = Student.objects.create(**validated_data)
        if report_card_data and report_card_data.get('report_card_file'):
            ReportCard.objects.create(student=student, **report_card_data)
        return student


class ReportCardEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportCard
        fields = ['report_card_file', 'student']


class StudentForAdvisorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name', 'is_state_choose_booklet_rows_done']

class AdvisorListSerializer(serializers.ModelSerializer):
    students_with_booklet_done = serializers.SerializerMethodField()
    total_students = serializers.SerializerMethodField()

    class Meta:
        model = Advisor
        fields = ['id', 'name', 'total_students', 'students_with_booklet_done']

    def get_total_students(self, obj):
        return Student.objects.filter(student_advisor=obj).count()

    def get_students_with_booklet_done(self, obj):
        return Student.objects.filter(student_advisor=obj, is_state_choose_booklet_rows_done=True).count()


class AdvisorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advisor
        fields = ['first_name', 'last_name', 'mobile']

class AdvisorCreationSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    mobile = serializers.CharField(max_length=11)
    student_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )

    def create(self, validated_data):
        student_ids = validated_data.pop('student_ids', [])
        user = self.context['request'].user
        manager = Manager.objects.get(mobile=user.mobile)
        advisor = Advisor.objects.create(manager_field=manager, is_advisor=True, **validated_data)

        if student_ids:
            students = Student.objects.filter(id__in=student_ids)
            for student in students:
                student.student_advisor = advisor
                student.save()

        return advisor

    def to_representation(self, instance):
        return AdvisorCreateSerializer(instance).data


class UserNoAdvisorSerializer(serializers.ModelSerializer):
    field_of_study = serializers.SerializerMethodField("get_field_of_study")
    province = serializers.SlugRelatedField(slug_field="title", read_only=True)
    gender = serializers.SerializerMethodField("get_gender")

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
            "field_of_study",
            "province",
            "gender",
        ]

class AdvisorIdSerializer(serializers.ModelSerializer):
    student_ids = serializers.SerializerMethodField()

    class Meta:
        model = Advisor
        fields = ['id', 'first_name', 'last_name', 'mobile', 'student_ids']

    def get_student_ids(self, obj):
        return list(obj.student_set.values_list('id', flat=True))


class AdvisorUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    mobile = serializers.CharField(max_length=11, required=False)
    student_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )

    def update(self, instance, validated_data):
        student_ids = validated_data.pop('student_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()

        if student_ids is not None:
            # Clear current advisor assignments for the advisor
            Student.objects.filter(student_advisor=instance).update(student_advisor=None)
            
            # Assign new students
            students = Student.objects.filter(id__in=student_ids)
            for student in students:
                student.student_advisor = instance
                student.save()
        
        return instance

    def to_representation(self, instance):
        return AdvisorCreateSerializer(instance).data


class UpdateMbtiResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['mbti_result', 'f_count', 'f_percentage', 'i_count', 'i_percentage', 'e_count', 'e_percentage', 'j_count', 'j_percentage', 'n_count', 'n_percentage', 'p_count', 'p_percentage', 's_count', 's_percentage', 't_count', 't_percentage']

    def update(self, instance, validated_data):
        instance.mbti_result = validated_data.get('mbti_result', instance.mbti_result)
        instance.f_count = validated_data.get('f_count', instance.f_count)
        instance.f_percentage = validated_data.get('f_percentage', instance.f_percentage)
        instance.i_count = validated_data.get('i_count', instance.i_count)
        instance.i_percentage = validated_data.get('i_percentage', instance.i_percentage)
        instance.e_count = validated_data.get('e_count', instance.e_count)
        instance.e_percentage = validated_data.get('e_percentage', instance.e_percentage)
        instance.j_count = validated_data.get('j_count', instance.j_count)
        instance.j_percentage = validated_data.get('j_percentage', instance.j_percentage)
        instance.n_count = validated_data.get('n_count', instance.n_count)
        instance.n_percentage = validated_data.get('n_percentage', instance.n_percentage)
        instance.p_count = validated_data.get('p_count', instance.p_count)
        instance.p_percentage = validated_data.get('p_percentage', instance.p_percentage)
        instance.s_count = validated_data.get('s_count', instance.s_count)
        instance.s_percentage = validated_data.get('s_percentage', instance.s_percentage)
        instance.t_count = validated_data.get('t_count', instance.t_count)
        instance.t_percentage = validated_data.get('t_percentage', instance.t_percentage)
        instance.save()
        return instance
    

class UserMbtiResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'mbti_result',
            'f_count',
            'f_percentage',
            'i_count',
            'i_percentage',
            'e_count',
            'e_percentage',
            'j_count',
            'j_percentage',
            'n_count',
            'n_percentage',
            'p_count',
            'p_percentage',
            's_count',
            's_percentage',
            't_count',
            't_percentage'
        ]
