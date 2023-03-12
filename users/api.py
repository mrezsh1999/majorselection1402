import pyotp as pyotp
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from users.models import Student, User, Advisor
from users.serializers import StudentLoginSerializer, AdvisorLoginSerializer, StudentListSerializer, \
    StudentRetrieveListSerializer


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_student is True


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_manager is True


class IsAdvisor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_advisor is True


class UserViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  GenericViewSet):
    OTP = None
    model = Student
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['field_of_study']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return StudentRetrieveListSerializer
        else:
            return StudentListSerializer

    def get_queryset(self):
        if self.request.user.is_advisor:
            return Student.objects.filter(student_advisor=self.request.user)
        elif self.request.user.is_manager:
            return Student.objects.filter(student_advisor__manager_field=self.request.user)

    @action(detail=False, methods=['POST'])
    def login(self, request):
        mobile = request.data.get('mobile')
        try:
            user = User.objects.get(mobile=mobile)
            otp_key = pyotp.random_base32()
            UserViewSet.OTP = pyotp.TOTP(otp_key, interval=120, digits=4)
            # kavenegar.send_otp(mobile, UserViewSet.OTP.now())
            return Response({'message': 'OTP was sent', 'otp': UserViewSet.OTP.now()}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'message': 'There is no user with this phone number'},
                            status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['POST'])
    def verify(self, request):
        mobile = request.data.get('mobile')
        if User.objects.filter(mobile=mobile, is_student=True):
            if UserViewSet.OTP.verify(request.data['otp']):
                student = Student.objects.get(mobile=mobile)
                serializer = StudentLoginSerializer(student)
                return Response(serializer.data, status=status.HTTP_200_OK)

            else:
                return Response('OTP is wrong/expired', status=status.HTTP_400_BAD_REQUEST)

        elif User.objects.filter(mobile=mobile, is_advisor=True):
            if UserViewSet.OTP.verify(request.data['otp']):
                advisor = Advisor.objects.get(mobile=mobile)
                serializer = AdvisorLoginSerializer(advisor)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response('OTP is wrong/expired', status=status.HTTP_400_BAD_REQUEST)

        elif User.objects.filter(mobile=mobile, is_manager=True):
            if UserViewSet.OTP.verify(request.data['otp']):
                advisor = Advisor.objects.get(mobile=mobile)
                serializer = AdvisorLoginSerializer(advisor)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response('OTP is wrong/expired', status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('user does not exist', status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        token = request.auth
        token.delete()
        return Response({
            'status': 'No Connect',
            'message': 'Successfully logout.'
        }, status=status.HTTP_204_NO_CONTENT)