from rest_framework import serializers
from .models import *
import re
from django.core.mail import send_mail
import random
from django.utils import timezone


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'fio', 'email', 'password', 'phone_number', 'gender_status', 'birthday', 'country', 'city', 'position', 'image']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = UserProfile.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        """
        Проверка совпадения нового пароля и его подтверждения.
        """
        new_password = data.get('new_password')
        confirm_new_password = data.get('confirm_new_password')

        if new_password != confirm_new_password:
            raise serializers.ValidationError({'confirm_new_password': 'New passwords do not match.'})

        # Дополнительные проверки сложности пароля
        if len(new_password) < 8:
            raise serializers.ValidationError({'new_password': 'Password must be at least 8 characters long.'})
        if not any(char.isdigit() for char in new_password):
            raise serializers.ValidationError({'new_password': 'Password must contain at least one digit.'})
        if not any(char.isalpha() for char in new_password):
            raise serializers.ValidationError({'new_password': 'Password must contain at least one letter.'})

        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Сериализатор для запроса сброса пароля.
    Валидирует только наличие пользователя с указанным email.
    """
    email = serializers.EmailField()

    def validate_email(self, email):
        try:
            # Проверяем существование пользователя
            UserProfile.objects.get(email=email)
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError("Пользователь с таким email не найден")

        # Инвалидируем предыдущие неиспользованные токены
        PasswordResetToken.objects.filter(
            user__email=email,
            is_used=False
        ).update(is_used=True)

        return email




class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Сериализатор для подтверждения сброса пароля.
    Выполняет расширенную валидацию нового пароля и токена.
    """
    email = serializers.EmailField()
    reset_code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(
        min_length=8,
        max_length=128,
        write_only=True
    )

    def validate_new_password(self, password):
        """
        Многоуровневая проверка сложности пароля.
        """
        # Проверка на наличие заглавной буквы
        if not re.search(r'[A-Z]', password):
            raise serializers.ValidationError(
                "Пароль должен содержать хотя бы одну заглавную букву"
            )

        # Проверка на наличие строчной буквы
        if not re.search(r'[a-z]', password):
            raise serializers.ValidationError(
                "Пароль должен содержать хотя бы одну строчную букву"
            )

        # Проверка на наличие цифры
        if not re.search(r'\d', password):
            raise serializers.ValidationError(
                "Пароль должен содержать хотя бы одну цифру"
            )

        # Проверка на наличие спецсимвола
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise serializers.ValidationError(
                "Пароль должен содержать хотя бы один специальный символ"
            )

        return password

    def validate(self, data):
        """
        Комплексная валидация токена сброса пароля.
        """
        try:
            # Находим пользователя
            user = UserProfile.objects.get(email=data['email'])

            # Проверяем токен сброса пароля
            reset_token = PasswordResetToken.objects.filter(
                user=user,
                token=data['reset_code'],
                is_used=False
            ).first()

            # Проверка существования токена
            if not reset_token:
                raise serializers.ValidationError("Неверный код восстановления")

            # Проверка срока действия токена
            if reset_token.is_expired():
                reset_token.is_used = True
                reset_token.save()
                raise serializers.ValidationError("Код восстановления истек")

        except UserProfile.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден")

        return data




class UserProfileFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['fio', 'image']





class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'fio', 'image', 'phone_number', 'gender_status', 'birthday', 'country', 'city', 'position' ]


class VisaCartCreateSerializer(serializers.ModelSerializer):
    # graduation_date = serializers.DateField(format=('%M-%Y'))
    class Meta:
        model = VisaCart
        fields = ['user', 'bank_cart', 'number_cart', 'graduation_date', 'csv']


class VisaCartSerializer(serializers.ModelSerializer):
    graduation_date = serializers.DateField(format=('%M-%Y'))
    class Meta:
        model = VisaCart
        fields = ['number_cart', 'graduation_date', 'bank_cart']


class VisaCartPodpiskiSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisaCart
        fields = ['number_cart',]


class TariffInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TariffInfo
        fields = ['id', 'info']



class TariffListSerializer(serializers.ModelSerializer):
    tariff_info = TariffInfoSerializer(many=True, read_only=True)
    class Meta:
        model = Tariff
        fields = ['id', 'term_status', 'sum', 'tariff_pay', 'tariff_info']



class TariffForCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff
        fields = ['term_status', 'status', 'sum']

class TariffForPaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff
        fields = ['term_status', 'sum']


class UserTariffSerializer(serializers.ModelSerializer):
    tariff = TariffForCartSerializer()
    user_tariff_pay = VisaCartPodpiskiSerializer()
    end_date = serializers.DateField(format=('%D-%M-%Y'))
    class Meta:
        model = UserTariff
        fields = ['tariff', 'user_tariff_pay', 'end_date']








class MPQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainPageQuestions
        fields = ['question', 'answer']


class MPSerializer(serializers.ModelSerializer):
    question_main_page = MainPageQuestions()
    class Meta:
        model = MainPage
        fields = ['title, description, question_main_page']

class AboutUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutUs
        fields = ['title', 'description1', 'description2', 'image1', 'image2', 'title_serti', 'description_serti',
                  'image_serti']
class AboutSchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutSchool
        fields = ['title1', 'description1', 'title2', 'description2']













class PatternSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pattern
        fields = ['patterns']




class Keys2Serializer(serializers.ModelSerializer):
    class Meta:
        model = Keys2
        fields = ['id', 'keys']

class KeysSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keys
        fields = ['id', 'key']

class StatyaListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statya
        fields = ['id', 'title', 'date', 'image', 'pattern']

class StatyaPrivateSerializer(serializers.ModelSerializer):
    keys_statya = KeysSerializer(many=True, read_only=True)
    keys_statya2 = Keys2Serializer(many=True, read_only=True)
    class Meta:
        model = Statya
        fields = ['id', 'title', 'description',  'date', 'image','for_key_description', 'keys_statya','description1', 'description2', 'description3','for_key_description2', 'keys_statya2']

class StatyaPublicSerializer(serializers.ModelSerializer):
    keys_statya = KeysSerializer(many=True, read_only=True)
    class Meta:
        model = Statya
        fields = ['id', 'title', 'description',  'date', 'image', 'for_key_description', 'keys_statya']











class MaterialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Materials
        fields = ['name']

class ProgrammaMasterClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgrammaMasterClass
        fields = ['name_master']

class ProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = ['title', 'description']

class PMCVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateMasterClassVideo
        fields = ['name', 'video']

class PMCKey1Serializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateMasterClassKey1
        fields = ['name']

class PMCKey2Serializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateMasterClassKey2
        fields = ['name']

class PMCQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasterQuestions
        fields = ['questions', 'answer']


class MasterPublicSerializer(serializers.ModelSerializer):
    private_video_mc = PMCVideoSerializer(many=True, read_only=True)
    private_master_key1 = PMCKey1Serializer(many=True, read_only=True)
    private_master_key2 = PMCKey2Serializer(many=True, read_only=True)
    questions_master_class = PMCQuestionSerializer(many=True, read_only=True)
    class Meta:
        model = MasterClass
        fields = ['id', 'private_title', 'private_description', 'private_video_mc', 'private_title2', 'private_master_key1', 'private_title3', 'private_master_key2',
                  'questions_master_class',]


class MasterPrivateSerializer(serializers.ModelSerializer):
    materials = MaterialsSerializer(many=True, read_only=True)
    programma_master_classes = ProgrammaMasterClassSerializer(many=True, read_only=True)
    master_classes = ProcessSerializer(many=True, read_only=True)
    questions_master_class = PMCQuestionSerializer(many=True, read_only=True)
    class Meta:
        model = MasterClass
        fields = ['id', 'title', 'description', 'dostup', 'count_lesson', 'price','title_about_master', 'description_about_master_class',
                  'materials', 'programma_master_classes', 'image_master', 'full_name', 'position', 'title_process', 'description_process', 'master_classes', 'title_questions', 'questions_master_class']


class MasterClassListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasterClass
        fields = ['id', 'title', 'description', 'pattern']


class MasterClassPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasterClass
        fields = ['id', 'title', 'description']














class WhoForCoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhoForCours
        fields = ['id', 'name']

class YouLearnSerializer(serializers.ModelSerializer):
    class Meta:
        model = YouLearn
        fields = ['id', 'name']

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['id', 'module_num', 'description']


class ProcessLearnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process_learn
        fields = ['id', 'number', 'title', 'description']

class CourseQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseQuestions
        fields = ['questions', 'answer']


class PrivateCourseVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateCourseVideo
        fields = ['module','name','video']


class CoursePublicSerializer(serializers.ModelSerializer):
    who_for_course = WhoForCoursSerializer(many=True, read_only=True)
    you_learns = YouLearnSerializer(many=True, read_only=True)
    modules = ModuleSerializer(many=True, read_only=True)
    course_pl = ProcessLearnSerializer(many=True, read_only=True)
    questions_course = CourseQuestionsSerializer(many=True, read_only=True)

    class Meta:
        model = Cours
        fields = ['id', 'title', 'description', 'dostup_course', 'count_module', 'count_materials', 'price', 'description1', 'description2', 'description3','who_for_course', 'you_learns',
                 'description4', 'description5', 'modules', 'image_prepod',
                  'full_name', 'position', 'course_pl', 'questions_course','pattern']


class CoursePrivateSerializer(serializers.ModelSerializer):
    questions_course = CourseQuestionsSerializer(many=True, read_only=True)
    private_video_course = PrivateCourseVideoSerializer(many=True, read_only=True)
    class Meta:
        model = Cours
        fields = ['id', 'title', 'description',
                 'questions_course', 'private_video_course']


class CoursListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cours
        fields = ['id', 'title', 'description', 'pattern']

class CourseForPaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Cours
        fields = ['title', 'price']


class CourseListForPaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Cours
        fields = ['id', 'title', 'description', ]




class UserCourseSerializer(serializers.ModelSerializer):
    user_course = CoursListSerializer(many=True, read_only=True)
    class Meta:
        model = UserCourse
        fields = ['user_course', 'purchase_date']



class FeedBackCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'user', 'course', 'text', 'created_date']

class FeedBackListSerializer(serializers.ModelSerializer):
    user = UserProfileFeedbackSerializer(read_only=True)
    class Meta:
        model = Feedback
        fields = ['id', 'user', 'course', 'text', 'created_date']

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['user', 'course', 'parent', 'text', 'created_date']

class CommentUserListSerializer(serializers.ModelSerializer):
    user = UserProfileFeedbackSerializer()
    class Meta:
        model = Comment
        fields = ['user', 'course', 'text', 'created_date']


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['course', 'master_class']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)  # Для отображения связанных CartItem

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items']


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = ['id', 'course', 'tariff', 'fio', 'email', 'phone','card_number', 'card_expiry',
                  'card_cvv', 'payment_method','created_at']

    def validate(self, data):
        # Убедиться, что пользователь оплачивает либо курс, либо тариф, но не оба
        if 'course' in data and 'tariff' in data:
            if data['course'] and data['tariff']:
                raise serializers.ValidationError("Пользователь не может оплачивать одновременно курс и тариф")
        return data

    def create(self, validated_data):
        # Создание платежа с привязкой к курсу или тарифу
        if 'course' in validated_data and validated_data['course']:
            payment = Payment.objects.create(course=validated_data['course'], **validated_data)
        elif 'tariff' in validated_data and validated_data['tariff']:
            payment = Payment.objects.create(tariff=validated_data['tariff'], **validated_data)
        else:
            payment = Payment.objects.create(**validated_data)
        return payment




class PaymentCourseSerializer(serializers.ModelSerializer):
    course = CourseListForPaySerializer(read_only=True)
    class Meta:
        model = Payment
        fields = ['id', 'course']


class PaymentTariffSerializer(serializers.ModelSerializer):
    tariff = TariffListSerializer(read_only=True)
    class Meta:
        model = Payment
        fields = ['id', 'tariff']


class PaymentMasterClassSerializer(serializers.ModelSerializer):
    master_class = MasterClassPaymentSerializer(read_only=True)
    class Meta:
        model = Payment
        fields = ['id', 'master_class']