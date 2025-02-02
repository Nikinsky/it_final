from rest_framework import generics, viewsets, status, permissions
from .serializers import *
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.contrib.auth.models import update_last_login
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import update_session_auth_hash
from .serializers import ChangePasswordSerializer

from rest_framework.exceptions import ValidationError, server_error
from it_education import *
from django.utils import timezone





class ChangePasswordView(generics.UpdateAPIView):
    """
    Изменение пароля текущего пользователя.
    """
    queryset = UserProfile.objects.all()
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Возвращает текущего пользователя.
        """
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        # Проверка старого пароля
        if not user.check_password(serializer.validated_data.get('old_password')):
            raise ValidationError({'old_password': 'Incorrect old password.'})

        # Установка нового пароля
        user.set_password(serializer.validated_data.get('new_password'))
        user.save()

        # Обновление сессии
        update_session_auth_hash(request, user)

        return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)



class RegisterView(generics.GenericAPIView):
    """Регистрация нового пользователя с выдачей токенов"""
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Генерация токенов
        refresh = RefreshToken.for_user(user)
        tokens = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        return Response(
            {
                "message": "User registered successfully.",
                "tokens": tokens,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(generics.GenericAPIView):
    """Авторизация пользователя по email с выдачей токенов"""
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {"error": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = UserProfile.objects.get(email=email)
        except UserProfile.DoesNotExist:
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = authenticate(username=user.username, password=password)
        if user is None:
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        tokens = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        return Response(
            {
                "message": "Login successful.",
                "tokens": tokens,
            },
            status=status.HTTP_200_OK,
        )


from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers


# Создаем сериализатор для токена обновления
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)


class LogoutView(generics.GenericAPIView):
    """Логаут пользователя"""
    serializer_class = LogoutSerializer

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            # Валидируем входные данные через сериализатор
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            refresh_token = serializer.validated_data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "Logout successful."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
import random
from django.core.mail import send_mail
from .models import PasswordResetToken


class PasswordResetRequestView(generics.GenericAPIView):
    """
    View для запроса сброса пароля.
    Генерирует и отправляет 6-значный код на email.
    """
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Используем сериализатор для валидации email
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Получаем email из провалидированных данных
        email = serializer.validated_data['email']

        # Находим пользователя
        user = UserProfile.objects.get(email=email)

        # Генерируем 6-значный код
        reset_code = str(random.randint(100000, 999999))

        # Создаем токен сброса пароля
        PasswordResetToken.objects.create(
            user=user,
            token=reset_code
        )

        # Отправляем код по почте
        send_mail(
            'Сброс пароля',
            f'Ваш код для сброса пароля: {reset_code}. Код действителен 1 час.',
            'e.osmonkulov@yandex.ru',
            [email],
            fail_silently=False,
        )

        return Response(
            {"message": "Код для сброса пароля отправлен"},
            status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    """
    View для подтверждения сброса пароля.
    Проверяет код и устанавливает новый пароль.
    """
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Используем сериализатор для полной валидации
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Извлекаем данные из провалидированного сериализатора
        email = serializer.validated_data['email']
        new_password = serializer.validated_data['new_password']

        # Находим пользователя
        user = UserProfile.objects.get(email=email)

        # Устанавливаем новый пароль
        user.set_password(new_password)
        user.save()

        # Инвалидируем использованный токен
        PasswordResetToken.objects.filter(
            user=user,
            token=serializer.validated_data['reset_code']
        ).update(is_used=True)

        return Response(
            {"message": "Пароль успешно изменен"},
            status=status.HTTP_200_OK
        )




class UserProfileListteyView(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        return UserProfile.objects.filter(id=self.request.user.id)

class UserProfileView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        return UserProfile.objects.filter(id=self.request.user.id)

class VisaCartListView(generics.ListAPIView):
    queryset = VisaCart.objects.all()
    serializer_class = VisaCartSerializer

    def get_queryset(self):
        return VisaCart.objects.filter(user__id=self.request.user.id)

class VisaCartDeleteView(generics.DestroyAPIView):
    queryset = VisaCart.objects.all()
    serializer_class = VisaCartSerializer


class VisaCartRetDeleteView(generics.RetrieveDestroyAPIView):
    queryset = VisaCart.objects.all()
    serializer_class = VisaCartSerializer

class VisaCartCreateView(generics.CreateAPIView):
    queryset = VisaCart.objects.all()
    serializer_class = VisaCartCreateSerializer

class TariffView(generics.ListAPIView):
    queryset = Tariff.objects.all()
    serializer_class = TariffListSerializer


class UserTariffListView(generics.ListAPIView):
    queryset = UserTariff.objects.all()
    serializer_class = UserTariffSerializer

    def get_queryset(self):
        return UserTariff.objects.filter(user__id=self.request.user.id)


class UserCourseListView(generics.ListAPIView):
    queryset = UserCourse.objects.all()
    serializer_class = UserCourseSerializer

    def get_queryset(self):
        return UserCourse.objects.filter(user__id=self.request.user.id)






class AboutUSListView(generics.ListAPIView):
    queryset = AboutUs.objects.all()
    serializer_class = AboutUsSerializer

class AboutSchoolListView(generics.ListAPIView):
    queryset = AboutSchool.objects.all()
    serializer_class = AboutSchoolSerializer


# class BaseContentViewSet(viewsets.ModelViewSet):
#     """
#     Базовый ViewSet для работы с контентом.
#     Содержит общую логику проверки доступа и обработки запросов.
#     """
#
#     def has_active_tariff(self):
#         """Проверяет наличие активного тарифа у пользователя"""
#         return UserTariff.objects.filter(
#             user=self.request.user,
#             is_active=True,
#             end_date__gt=timezone.now()
#         ).exists()
#
#     def get_serializer_context(self):
#         """Добавляет информацию о доступе в контекст сериализатора"""
#         context = super().get_serializer_context()
#         context['has_access'] = self.has_active_tariff()
#         return context

class BaseContentViewSet(viewsets.ModelViewSet):
    """
    Базовый ViewSet для работы с контентом.
    """

    def has_active_tariff(self):
        """Проверяет наличие активного тарифа у пользователя"""
        # Проверяем сначала авторизацию
        if not self.request.user.is_authenticated:
            return False

        return UserTariff.objects.filter(
            user=self.request.user,
            is_active=True,
            end_date__gt=timezone.now()
        ).exists()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['has_access'] = self.has_active_tariff()
        return context



class StatyaViewSet(BaseContentViewSet):
    """ViewSet для работы со статьями"""
    queryset = Statya.objects.all()

    def get_serializer_class(self):
        """Выбирает подходящий сериализатор в зависимости от наличия подписки"""
        if self.has_active_tariff():
            return StatyaPrivateSerializer
        return StatyaPublicSerializer


class StatyaListView(generics.ListAPIView):
    queryset = Statya.objects.all()
    serializer_class = StatyaListSerializer





class MasterClasslView(BaseContentViewSet):
    queryset = MasterClass.objects.all()

    def get_serializer_class(self):
        """Выбирает подходящий сериализатор в зависимости от наличия подписки"""
        if self.has_active_tariff():
            return MasterPrivateSerializer
        return MasterPublicSerializer


class MasterClassListView(generics.ListAPIView):
    queryset = MasterClass.objects.all()
    serializer_class = MasterClassListSerializer









class CoursListView(generics.ListAPIView):
    queryset = Cours.objects.all()
    serializer_class = CoursListSerializer


class CourseViewSet(BaseContentViewSet):
    queryset = Cours.objects.all()
    serializer_class = CoursePublicSerializer

    def get_serializer_class(self):
        if hasattr(self, 'action') and self.action == 'list':
            return CoursePublicSerializer

        # Сначала проверяем аутентификацию
        if not self.request.user.is_authenticated:
            return CoursePublicSerializer

        try:
            user_course = UserCourse.objects.get(user=self.request.user, course=self.get_object())
            return CoursePrivateSerializer
        except UserCourse.DoesNotExist:
            return CoursePublicSerializer

    def list(self, request):
        courses = self.get_queryset()
        purchased = set()  # По умолчанию пустой set

        # Получаем купленные курсы только для авторизованных пользователей
        if request.user.is_authenticated:
            purchased = set(UserCourse.objects.filter(
                user=request.user
            ).values_list('course_id', flat=True))

        data = []
        for course in courses:
            serializer = (CoursePrivateSerializer if course.id in purchased
                          else CoursePublicSerializer)
            course_data = serializer(course).data
            course_data['has_purchased'] = course.id in purchased

            if not course_data['has_purchased']:
                course_data['purchase_info'] = {
                    'price': course.price,
                    'message': 'Приобретите курс для полного доступа'
                }
            data.append(course_data)

        return Response(data)

    @action(detail=True, methods=['post'])
    def purchase(self, request, pk=None):
        if not request.user.is_authenticated:
            return Response({'error': 'Требуется авторизация'}, status=401)

        course = self.get_object()
        if UserCourse.objects.filter(user=request.user, course=course).exists():
            return Response({'error': 'Курс уже куплен'}, status=400)

        UserCourse.objects.create(user=request.user, course=course)
        return Response({'status': 'success'})











class FeedBackCreateView(generics.CreateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedBackCreateSerializer


class FeedBackListView(generics.ListAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedBackListSerializer



class CommentListView(generics.ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentUserListSerializer

class CommentCreateView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentCreateSerializer

class CartItemViewSet(generics.ListCreateAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer


class CartViewSet(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    # def get_queryset(self):
    #     return Cart.objects.filter(user__id=self.request.user.id)



class PaymentCreateView(generics.CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def perform_create(self, serializer):
        # Здесь можно добавить дополнительную логику перед сохранением платежа
        serializer.save()

class PaymentListView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_queryset(self):
        # Здесь можно добавить фильтрацию или другую логику
        return self.queryset.order_by('-created_at')


class PaymentCartCourseView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentCourseSerializer


class PaymentCartTariffView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentTariffSerializer

class PaymentCartMasterClassView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = MasterClassPaymentSerializer
