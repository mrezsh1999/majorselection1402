import os

import pyotp as pyotp
from django.http import HttpResponse, Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny
from .kavenegar import send_otp
import pandas as pd
from booklet_information.models import Province
from django.db import models
from majorselection1402 import settings
from django.db.models import Count
from users.models import Student, User, Advisor, ReportCard, Manager, School
from users.serializers import (
    StudentLoginSerializer,
    AdvisorLoginSerializer,
    StudentListSerializer,
    StudentListSerializerAdvisor,
    StudentListSerializerManager,
    StudentListSerializerManagerNew,
    StudentRetrieveListSerializer,
    ReportCardSerializer,
    ReportCardEditSerializer,
    AdvisorListSerializer,
    StudentCreationSerializer,
    StudentUploadSerializer,
    AdvisorUploadSerializer,
    AdvisorCreationSerializer,
    UserNoAdvisorSerializer,
    AdvisorIdSerializer,
    AdvisorUpdateSerializer,
    StudentUpdateSerializer,
    UpdateMbtiResultSerializer,
    UserMbtiResultSerializer
)


def convert_persian_digits_to_int(input_str):
    num_dic = {
        '۰': '0',
        '۱': '1',
        '۲': '2',
        '۳': '3',
        '۴': '4',
        '۵': '5',
        '۶': '6',
        '۷': '7',
        '۸': '8',
        '۹': '9',
    }

    return str(''.join(num_dic.get(char, char) for char in input_str))

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_student is True


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_manager is True


class IsAdvisor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_advisor is True


class UserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    OTP = None
    model = Student
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ["field_of_study"]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_serializer_class(self):
        if self.action == "retrieve":
            return StudentRetrieveListSerializer
        else:
            if self.request.user.is_advisor:
                return StudentListSerializerAdvisor
            elif self.request.user.is_manager:
                return StudentListSerializerManagerNew
            elif self.request.user.is_student:
                return StudentRetrieveListSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_queryset(self):
        if self.request.user.is_advisor:
            return Student.objects.filter(student_advisor=self.request.user).order_by("field_of_study", "last_name")
        elif self.request.user.is_manager:
            manager = Manager.objects.get(id=self.request.user.id)
            school = manager.school_set.first()
            return Student.objects.filter(
                school=school
            ).order_by("student_advisor__last_name", "field_of_study", "last_name").order_by('process_start_time')
        else:
                return Student.objects.all()
        
    @action(detail=False, methods=["GET"], permission_classes=[AllowAny])
    def advisor_list(self, request):
        advisors = Advisor.objects.filter(manager_field=request.user).annotate(total_students=Count('student'))
        advisors = advisors.order_by('-total_students')  # Order advisors based on total stud
        serializer = AdvisorListSerializer(advisors, many=True)
        return Response(serializer.data)
    

    @action(detail=False, methods=["POST"], permission_classes=[AllowAny])
    def login(self, request):
        mobile = request.data.get("mobile")
        mobile = convert_persian_digits_to_int(mobile)
        try:
            user = User.objects.get(mobile=mobile)
            otp_key = pyotp.random_base32()
            OTP = pyotp.TOTP(otp_key, interval=120, digits=4)
            user.otp_key = otp_key
            user.save()
            # UserViewSet.OTP = pyotp.TOTP(otp_key, interval=120, digits=4)
            send_otp(mobile, OTP.now())
            return Response(
                {"message": "OTP was sent", "otp": OTP.now()},
                status=status.HTTP_200_OK,
            )

        except User.DoesNotExist:
            return Response(
                {"message": "There is no user with this phone number"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=False, methods=["POST"], permission_classes=[AllowAny])
    def verify(self, request):
        mobile = request.data.get("mobile")
        mobile = convert_persian_digits_to_int(mobile)
        if User.objects.filter(mobile=mobile, is_student=True):
            otp_key = User.objects.get(mobile=mobile).otp_key
            OTP = pyotp.TOTP(otp_key, interval=120, digits=4)
            if OTP.verify(convert_persian_digits_to_int(request.data["otp"])):
                student = Student.objects.get(mobile=mobile)
                serializer = StudentLoginSerializer(student)
                return Response(serializer.data, status=status.HTTP_200_OK)

            else:
                return Response(
                    "OTP is wrong/expired", status=status.HTTP_400_BAD_REQUEST
                )

        elif User.objects.filter(mobile=mobile, is_advisor=True):
            otp_key = User.objects.get(mobile=mobile).otp_key
            OTP = pyotp.TOTP(otp_key, interval=120, digits=4)
            if OTP.verify(convert_persian_digits_to_int(request.data["otp"])):
                advisor = Advisor.objects.get(mobile=mobile)
                serializer = AdvisorLoginSerializer(advisor)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    "OTP is wrong/expired", status=status.HTTP_400_BAD_REQUEST
                )

        elif User.objects.filter(mobile=mobile, is_manager=True):
            otp_key = User.objects.get(mobile=mobile).otp_key
            OTP = pyotp.TOTP(otp_key, interval=120, digits=4)
            if OTP.verify(convert_persian_digits_to_int(request.data["otp"])):
                manager = Manager.objects.get(mobile=mobile)
                serializer = AdvisorLoginSerializer(manager)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    "OTP is wrong/expired", status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response("user does not exist", status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["POST"], permission_classes=[AllowAny])
    def logout(self, request):
        token = request.auth
        token.delete()
        return Response(
            {"status": "No Connect", "message": "Successfully logout."},
            status=status.HTTP_204_NO_CONTENT,
        )
    
    @action(detail=False, methods=["GET"], permission_classes=[AllowAny])
    def generate_students_txt(self, request):
        # Create a dictionary to store student names by school
        schools_with_students = {}

        # Get all schools
        schools = School.objects.all()

        # Iterate through each school and fetch students
        for school in schools:
            students = Student.objects.filter(school=school)
            student_names = [student.name for student in students]

            # Add school and its student names to the dictionary
            if student_names:
                schools_with_students[school.title] = student_names

        # Create a response object to write the file content
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="school_students.txt"'

        # Write the school and student names into the file
        for school, students in schools_with_students.items():
            response.write(f"School: {school}\n")
            response.write("\n".join(students))
            response.write("\n\n")

        return response
    
    @action(detail=False, methods=["GET"], permission_classes=[AllowAny])
    def export_students_xlsx(self, request):
        # Get students where is_state_choose_booklet_rows_done is True
        students = Student.objects.filter(is_state_choose_booklet_rows_done=True).select_related(
            'student_advisor__manager_field', 'school'
        )

        # Create list for storing data
        student_data = []

        for student in students:
            advisor_name = student.student_advisor.name if student.student_advisor else ""
            manager_name = student.student_advisor.manager_field.name if student.student_advisor and student.student_advisor.manager_field else ""
            school_name = student.school.title if student.school else ""
            student_data.append([
                student.name,
                advisor_name,
                manager_name,
                school_name
            ])

        # Define column names
        columns = ['دانش آموز', 'مشاور', 'مدیر', 'مجموعه آموزشی']

        # Create DataFrame
        df = pd.DataFrame(student_data, columns=columns)

        # Create a response object
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=students.xlsx'

        # Write the DataFrame to the response using ExcelWriter
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Students')

        return response
    
    @action(detail=False, methods=["GET"], permission_classes=[AllowAny])
    def export_students_xlsx_end(self, request):
        # Get students where is_state_choose_booklet_rows_done is True
        students = Student.objects.filter(process_end_time__isnull=False).select_related(
            'student_advisor__manager_field', 'school'
        )

        # Create list for storing data
        student_data = []

        for student in students:
            advisor_name = student.student_advisor.name if student.student_advisor else ""
            manager_name = student.student_advisor.manager_field.name if student.student_advisor and student.student_advisor.manager_field else ""
            school_name = student.school.title if student.school else ""
            student_data.append([
                student.name,
                advisor_name,
                manager_name,
                school_name
            ])

        # Define column names
        columns = ['دانش آموز', 'مشاور', 'مدیر', 'مجموعه آموزشی']

        # Create DataFrame
        df = pd.DataFrame(student_data, columns=columns)

        # Create a response object
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=students.xlsx'

        # Write the DataFrame to the response using ExcelWriter
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Students')

        return response
    

    @action(detail=False, methods=["GET"], permission_classes=[AllowAny])
    def export_students_xlsx_full(self, request):
        # Get all students
        students = Student.objects.select_related('student_advisor__manager_field', 'school')

        # Create list for storing data
        student_data = []

        for student in students:
            advisor_name = student.student_advisor.name if student.student_advisor else ""
            manager_name = student.student_advisor.manager_field.name if student.student_advisor and student.student_advisor.manager_field else ""
            school_name = student.school.title if student.school else ""
            is_state_choose_booklet_rows_done = "بله" if student.is_state_choose_booklet_rows_done else "خیر"
            process_end_time_status = "بله" if student.process_end_time else "خیر"

            student_data.append([
                student.name,
                advisor_name,
                manager_name,
                school_name,
                is_state_choose_booklet_rows_done,
                process_end_time_status
            ])

        # Define column names
        columns = ['دانش آموز', 'مشاور', 'مدیر', 'مجموعه آموزشی', 'تکمیل فرایند', 'فرایند تکمیل ولی انتخاب رشته خالی']

        # Create DataFrame
        df = pd.DataFrame(student_data, columns=columns)

        # Create a response object
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=all_students.xlsx'

        # Write the DataFrame to the response using ExcelWriter
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='All Students')

        return response

    @action(detail=False, methods=["POST"], permission_classes=[AllowAny])
    def create_student(self, request):
        if request.method == 'POST':
            # Pass the request context to the serializer
            serializer = StudentCreationSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=["POST"], permission_classes=[AllowAny])
    def create_group_advisors(self, request, *args, **kwargs):
        if not request.user.is_manager:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = AdvisorCreationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            advisor = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=["POST"], permission_classes=[IsAuthenticated])
    def update_advisor(self, request, pk=None):
        try:
            advisor = Advisor.objects.get(pk=pk)
        except Advisor.DoesNotExist:
            return Response(
                {"detail": "Advisor not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if not request.user.is_manager:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = AdvisorUpdateSerializer(advisor, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=["POST"], permission_classes=[IsAuthenticated])
    def update_student(self, request, pk=None):
        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return Response(
                {"detail": "Student not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if not request.user.is_manager:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = StudentUpdateSerializer(student, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=["GET"], permission_classes=[AllowAny])
    def get_users_without_advisor(self, request):
        students_without_advisor = Student.objects.filter(student_advisor__isnull=True)
        serializer = UserNoAdvisorSerializer(students_without_advisor, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["GET"], permission_classes=[AllowAny])
    def get_students_for_or_without_advisor(self, request):
        advisor_id = request.query_params.get('advisor_id')
        if advisor_id:
            manager = Manager.objects.get(id=request.user.id)
            school = manager.school_set.first()
            students = Student.objects.filter(
                models.Q(student_advisor__id=advisor_id) | (models.Q(student_advisor__isnull=True) & models.Q(school=school))
            )
        else:
            students = Student.objects.filter(student_advisor__isnull=True)
        
        serializer = UserNoAdvisorSerializer(students, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["GET"], permission_classes=[AllowAny])   
    def get_advisor_id(self, request):
        advisor_id = request.query_params.get('id')
        if not advisor_id:
            return Response({"error": "ID parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            advisor = Advisor.objects.get(id=advisor_id)
        except Advisor.DoesNotExist:
            return Response({"error": "Advisor not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AdvisorIdSerializer(advisor)
        return Response(serializer.data)
    
    @action(detail=False, methods=["POST"], permission_classes=[AllowAny])   
    def mbti_result(self, request, *args, **kwargs):
        student = Student.objects.get(mobile=request.user)
        serializer = UpdateMbtiResultSerializer(data=request.data, instance=student)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": "MBTI result updated successfully"},
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=["GET"], permission_classes=[AllowAny])   
    def get_mbti_result(self, request, *args, **kwargs):
        student = Student.objects.get(mobile=request.user)
        serializer = UserMbtiResultSerializer(student)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["GET"], permission_classes=[AllowAny])   
    def get_mbti_result_with_id(self, request, *args, **kwargs):
        student_id = request.query_params.get('student_id')
        if not student_id:
            return Response({"error": "student_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserMbtiResultSerializer(student)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["POST"], permission_classes=[AllowAny])
    def advisors_group(self, request):
        if not request.user.is_manager:
            return Response({'error': 'Only managers can upload advisors.'}, status=status.HTTP_403_FORBIDDEN)
        
        file = request.FILES['file']
        df = pd.read_excel(file)

        advisors = []
        for _, row in df.iterrows():
            first_name = row['نام']
            last_name = row['نام خانوادگی']
            mobile = row['شماره تماس']

            advisor_data = {
                'first_name': first_name,
                'last_name': last_name,
                'mobile': mobile,
                'is_advisor': True,
                'manager_field': request.user.id
            }

            try:
                advisor = Advisor.objects.get(mobile=mobile)
                serializer = AdvisorUploadSerializer(advisor, data=advisor_data)
            except Advisor.DoesNotExist:
                serializer = AdvisorUploadSerializer(data=advisor_data)

            if serializer.is_valid():
                advisors.append(serializer)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        for advisor in advisors:
            advisor.save()

        return Response({'message': 'Advisors processed successfully'}, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=["POST"], permission_classes=[AllowAny])
    def students_group(self, request):
        file = request.FILES['file']
        df = pd.read_excel(file)

        field_of_study_mapping = {
            "ریاضی": 0,
            "تجربی": 1,
            "انسانی": 2,
            "هنر": 3,
            "زبان": 4,
            "ریاضی 1": 5,
            "ریاضی و فیزیک": 6,
            "ریاضی جدید": 7
        }
        gender_mapping = {"مرد": True, "زن": False}

        manager = Manager.objects.get(id=request.user.id)
        school = manager.school_set.first()
        if not school:
            return Response({'error': 'Manager does not have an associated school'}, status=status.HTTP_400_BAD_REQUEST)

        students = []
        for _, row in df.iterrows():
            first_name = row['نام']
            last_name = row['نام خانوادگی']
            gender = gender_mapping.get(row['جنسیت'])
            mobile = row['شماره تماس']
            province_name = row['استان']
            field_of_study = field_of_study_mapping.get(row['رشته'])

            try:
                province = Province.objects.get(title=province_name)
            except Province.DoesNotExist:
                return Response({'error': f'Province {province_name} does not exist'}, status=status.HTTP_400_BAD_REQUEST)
                

            student_data = {
                'first_name': first_name,
                'last_name': last_name,
                'mobile': mobile,
                'gender': gender,
                'province': province.id,
                'field_of_study': field_of_study,
                'is_student': True,
                'school': school.id
            }

            try:
                student = Student.objects.get(mobile=mobile)
                serializer = StudentUploadSerializer(student, data=student_data)
            except Student.DoesNotExist:
                serializer = StudentUploadSerializer(data=student_data)
            if serializer.is_valid():
                students.append(serializer)
            else:
                print(serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        for student in students:
            student.save()

        return Response({'message': 'Students created successfully'}, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=["POST"], permission_classes=[AllowAny])
    def upload_report_card(self, request):
        student_id = request.data.get('student')
        
        if not student_id:
            return Response({'error': 'Student ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Delete existing report card if exists
        existing_report_card = ReportCard.objects.filter(student=student)
        if existing_report_card.exists():
            existing_report_card.delete()

        # Save new report card
        serializer = ReportCardEditSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # @action(detail=False, methods=["GET"], permission_classes=[AllowAny])
    # def delete_all(self, request):
    #     Student.objects.all().delete()
    #     Advisor.objects.all().delete()
    #     return Response(
    #         {"status": "No Connect", "message": "Successfully logout."},
    #         status=status.HTTP_204_NO_CONTENT,
    #     )

    @action(detail=False, methods=["GET"])
    def pdf(self, request):
        try:
            path = ReportCard.objects.get(
                student_id=request.GET.get("student_id")
            ).report_card_file.path
            file_path = os.path.join(settings.MEDIA_ROOT, path)
            if os.path.exists(file_path):
                with open(file_path, "rb") as fh:
                    response = HttpResponse(fh.read(), content_type="application/pdf")
                    response[
                        "Content-Disposition"
                    ] = "inline; filename=" + os.path.basename(file_path)
                    return response
            raise Http404
        except ReportCard.DoesNotExist:
            raise Http404


class ReportCardViewSet(mixins.CreateModelMixin, GenericViewSet):
    model = ReportCard
    serializer_class = ReportCardSerializer

    def perform_create(self, serializer):
        student = Student.objects.get(id=self.request.user.id)
        serializer.save(student=student)
