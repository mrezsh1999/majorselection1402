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

from majorselection1402 import settings
from users.models import Student, User, Advisor, ReportCard, Manager
from users.serializers import (
    StudentLoginSerializer,
    AdvisorLoginSerializer,
    StudentListSerializer,
    StudentListSerializerAdvisor,
    StudentListSerializerManager,
    StudentRetrieveListSerializer,
    ReportCardSerializer,
)


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
                return StudentListSerializerManager

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_queryset(self):
        if self.request.user.is_advisor:
            return Student.objects.filter(student_advisor=self.request.user).order_by("field_of_study", "last_name")
        elif self.request.user.is_manager:
            return Student.objects.filter(
                student_advisor__manager_field=self.request.user
            ).order_by("student_advisor__last_name", "field_of_study", "last_name")

    @action(detail=False, methods=["POST"], permission_classes=[AllowAny])
    def login(self, request):
        mobile = request.data.get("mobile")
        try:
            user = User.objects.get(mobile=mobile)
            otp_key = pyotp.random_base32()
            OTP = pyotp.TOTP(otp_key, interval=120, digits=4)
            user.otp_key = otp_key
            user.save()
            # UserViewSet.OTP = pyotp.TOTP(otp_key, interval=120, digits=4)
            # send_otp(mobile, OTP.now())
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
        if User.objects.filter(mobile=mobile, is_student=True):
            otp_key = User.objects.get(mobile=mobile).otp_key
            OTP = pyotp.TOTP(otp_key, interval=120, digits=4)
            if OTP.verify(request.data["otp"]):
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
            if OTP.verify(request.data["otp"]):
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
            if OTP.verify(request.data["otp"]):
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
