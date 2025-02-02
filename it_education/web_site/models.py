from datetime import timezone
from multiprocessing.util import MAXFD

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail











class UserProfile(AbstractUser):
    fio = models.CharField(max_length=50, null=True, blank=True)
    phone_number = PhoneNumberField(null=True,blank=True)
    GENDER = (
        ('Мужской','Мужской'),
        ('Женский', 'Женский'),
    )
    gender_status = models.CharField(max_length=32, choices=GENDER,null=True,blank=True, verbose_name="Пол")
    image = models.ImageField(upload_to='image_user', null=True, blank=True)
    birthday = models.DateField(null=True,blank=True)
    country = models.CharField(max_length=50, null=True,blank=True)
    city = models.CharField(max_length=50, null=True,blank=True)
    position = models.CharField(max_length=50, null=True,blank=True)

    def __str__(self):
        return f'{self.username}'


from django.utils import timezone
from datetime import timedelta


class PasswordResetToken(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    token = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        # Токен действителен только 1 час
        return timezone.now() > self.created_at + timedelta(hours=1)










class VisaCart(models.Model):
    user = models.ForeignKey(UserProfile, related_name='visa_carts', on_delete=models.CASCADE)
    bank_cart = models.CharField(max_length=10, choices=[('visa', 'Visa'), ('mastercard', 'MasterCard')])
    number_cart = models.CharField(max_length=16,
                    validators=[
                        RegexValidator(r'\d{16}$', message="Введите все цифры карты")
                    ],
                    help_text="Введите номер банковской карты")
    graduation_date = models.DateField()
    csv = models.CharField(max_length=4)

    def __str__(self):
        return f"{self.user} - {self.number_cart}"




class Tariff(models.Model):
    TERM_CHOICES = (
        ('месяц +', 'месяц +'),
        ('год', 'год'),
        ('год+', 'год+'),
    )
    term_status = models.CharField(max_length=32, choices=TERM_CHOICES, default='месяц +')
    sum = models.PositiveIntegerField()
    TARIFF_PAY = (
        ("Ежемесячно", "Ежемесячно"),
        ("Ежемесячно", "Ежемесячно"),
        ("Ежегодно", "Ежегодно"),
    )
    tariff_pay = models.CharField(max_length=32, choices=TARIFF_PAY, default='Ежемесячно')
    STATUS_TARIFF = (
        ('Начальная', 'Начальная'),
        ('Про', 'Про'),
    )
    status = models.CharField(max_length=32, choices=STATUS_TARIFF)

    def __str__(self):
        return f'{self.term_status} -{self.status}'

    class Meta:
        verbose_name = 'Тариф'
        verbose_name_plural = 'Тарифы'

class TariffInfo(models.Model):
    tariff =models.ForeignKey(Tariff, related_name='tariff_info', on_delete=models.CASCADE)
    info = models.CharField(max_length=100)



class UserTariff(models.Model):
    """
    Модель для отслеживания активных тарифов пользователей.
    Связывает пользователей с их текущими тарифами и сроками действия.
    """
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='user_tariffs')
    tariff = models.ForeignKey(Tariff, on_delete=models.CASCADE, verbose_name='Тариф')
    start_date = models.DateTimeField(auto_now_add=True)
    visa_cart = models.ForeignKey(VisaCart, related_name='user_tariff_pay', on_delete=models.CASCADE)
    end_date = models.DateField(verbose_name='Дата окончания')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    def is_valid(self):
        """Проверяет, действителен ли тариф на текущий момент"""
        return self.is_active and self.end_date > timezone.now()

    def __str__(self):
        return f"{self.user.fio} - {self.tariff.status}"

    class Meta:
        verbose_name = 'Тариф пользователя'
        verbose_name_plural = 'Тарифы пользователей'


class UserCourse(models.Model):
    """Модель для отслеживания купленных пользователями курсов"""
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='purchased_courses')
    course = models.ForeignKey('Cours', related_name='user_course',on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'course']

    def __str__(self):
        return f'{self.user} - {self.course}'



















class MainPage(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()


class MainPageQuestions(models.Model):
    main_page = models.ForeignKey(MainPage, related_name='question_main_page', on_delete=models.CASCADE)
    question = models.CharField(max_length=250)
    answer = models.TextField()


class AboutSchool(models.Model):
    title1 = models.CharField(max_length=100,null=True, blank=True)
    description1 = models.TextField(null=True, blank=True)
    title2 = models.CharField(max_length=100, null=True, blank=True)
    description2 = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.title1}'


class AboutUs(models.Model):
    title = models.CharField(max_length=100)
    description1 = models.TextField(null=True, blank=True)
    description2 = models.TextField(null=True, blank=True)
    image1 = models.ImageField(upload_to='about_us', null=True, blank=True)
    image2 = models.ImageField(upload_to='about_us', null=True, blank=True)
    title_serti = models.CharField(max_length=100)
    description_serti = models.TextField(null=True, blank=True)
    image_serti = models.ImageField(upload_to='about_us',null=True, blank=True)


    def __str__(self):
        return f'{self.title}'





class Pattern(models.Model):
    PATTERN = (
        ('pattern 1' , 'pattern 1'),
        ('pattern 2 ','pattern 2 '),
    )
    patterns = models.CharField(max_length=25,choices=PATTERN)

    def __str__(self):
        return f'{self.patterns}'



class Statya(models.Model):
    title = models.CharField(max_length=255)
    description =models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='statya_images/')
    for_key_description = models.TextField(null=True,blank=True)
    description1 = models.TextField(null=True, blank=True)
    description2 = models.TextField(null=True, blank=True)
    description3 = models.TextField(null=True, blank=True)
    for_key_description2 =models.TextField(null=True,blank=True)
    date = models.DateField(auto_now_add=True)
    pattern = models.ForeignKey(Pattern,on_delete=models.CASCADE)

    # Добавляем поле для определения, требуется ли подписка для просмотра
    requires_subscription = models.BooleanField(
        default=True,
        help_text="Требуется ли подписка для просмотра полной статьи"
    )

    def __str__(self):
        return self.title

class Keys(models.Model):
    statya = models.ForeignKey(Statya, related_name='keys_statya', on_delete=models.CASCADE)
    key = models.CharField(max_length=255)



class Keys2(models.Model):
    statya = models.ForeignKey(Statya, related_name='keys_statya2', on_delete=models.CASCADE)
    keys = models.CharField(max_length=255)













class MasterClass(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField( null=True, blank=True)
    dostup = models.CharField(max_length=255, null=True, blank=True)
    count_lesson = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    title_about_master = models.CharField(max_length=100, null=True, blank=True)
    description_about_master_class = models.TextField( null=True, blank=True)
    image_master = models.ImageField(upload_to='master_class_images/', null=True, blank=True)
    full_name = models.CharField(max_length=100)
    position = models.CharField(max_length=255, null=True, blank=True)
    title_process = models.CharField(max_length=100, null=True,blank=True)
    description_process = models.TextField( null=True, blank=True)
    title_questions = models.CharField(max_length=100)
    pattern = models.ForeignKey(Pattern,on_delete=models.CASCADE)

    private_title = models.CharField(max_length=250)
    private_description = models.TextField(null=True, blank=True)
    private_title2 = models.CharField(max_length=255, null=True, blank=True)
    private_title3 = models.CharField(max_length=255,null=True, blank=True)
    # Добавляем поле для минимального требуемого уровня подписки
    requires_subscription = models.BooleanField(
        default=True,
        help_text="Требуется ли подписка для просмотра полной статьи"
    )

    def __str__(self):
        return self.title


class Materials(models.Model):
    master_class = models.ForeignKey(MasterClass, related_name='materials', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ProgrammaMasterClass(models.Model):
    name_master = models.CharField(max_length=255)
    master_class = models.ForeignKey(MasterClass, related_name='programma_master_classes', on_delete=models.CASCADE)

    def __str__(self):
        return self.name_master


class Process(models.Model):
    number = models.PositiveSmallIntegerField(default=1)
    title = models.CharField(max_length=255)
    description = models.TextField()
    master_class = models.ForeignKey(MasterClass, related_name='master_classes', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.number} - {self.title}'

class PrivateMasterClassVideo(models.Model):
    master_class = models.ForeignKey(MasterClass, related_name='private_video_mc', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    video = models.FileField(upload_to='video_master_class')


class PrivateMasterClassKey1(models.Model):
    master_class = models.ForeignKey(MasterClass, related_name='private_master_key1', on_delete=models.CASCADE)
    name = models.CharField(max_length=500)

class PrivateMasterClassKey2(models.Model):
    master_class = models.ForeignKey(MasterClass, related_name='private_master_key2', on_delete=models.CASCADE)
    name = models.CharField(max_length=500)


class MasterQuestions(models.Model):
    master_class = models.ForeignKey(MasterClass, related_name='questions_master_class', on_delete=models.CASCADE)
    questions = models.CharField(max_length=255)
    answer = models.TextField()








class Cours(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    dostup_course = models.CharField(max_length=250)
    count_module = models.CharField(max_length=100)
    count_materials = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2,)
    description1 = models.TextField(null=True, blank=True)
    description2 = models.TextField(null=True, blank=True)
    description3 = models.TextField(null=True, blank=True)
    description4 = models.TextField(null=True, blank=True)
    description5 = models.TextField(null=True, blank=True)
    image_prepod = models.ImageField(upload_to='course_img/')
    full_name = models.CharField(max_length=50,null=True, blank=True)
    position = models.CharField(max_length=50,null=True, blank=True)
    pattern = models.ForeignKey(Pattern,on_delete=models.CASCADE)


    private_title = models.CharField(max_length=500,null=True, blank=True)
    private_description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title


class WhoForCours(models.Model):
    name = models.CharField(max_length=500)
    course = models.ForeignKey(Cours, related_name='who_for_course', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class YouLearn(models.Model):
    name = models.CharField(max_length=500)
    course = models.ForeignKey(Cours, related_name='you_learns', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Module(models.Model):
    module_num = models.CharField(max_length=15)
    description = models.TextField()
    course = models.ForeignKey(Cours, related_name='modules', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.module_num}: {self.course.title}"

class Process_learn(models.Model):
    course = models.ForeignKey(Cours, related_name='course_pl', on_delete=models.CASCADE)
    number = models.PositiveIntegerField(null=True, blank=True)
    title = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)


class CourseQuestions(models.Model):
    master_class = models.ForeignKey(Cours, related_name='questions_course', on_delete=models.CASCADE)
    questions = models.CharField(max_length=255)
    answer = models.TextField()


class PrivateCourseVideo(models.Model):
    master_class = models.ForeignKey(Cours, related_name='private_video_course', on_delete=models.CASCADE)
    module = models.ForeignKey(Module, related_name='module_curse', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    video = models.FileField(upload_to='video_course')






class Cart(models.Model):
    user = models.OneToOneField(UserProfile, related_name='carts', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user}'



class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    course = models.ForeignKey(Cours, related_name='course_item', on_delete=models.CASCADE, null=True, blank=True)
    master_class = models.ForeignKey(MasterClass, related_name='master_class_item', on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return f"{self.cart} - {self.course}"


class Payment(models.Model):
    course = models.ForeignKey(Cours, related_name='payment_course', on_delete=models.CASCADE, null=True, blank=True)
    tariff = models.ForeignKey(Tariff, related_name='payment_tariff', on_delete=models.CASCADE, null=True, blank=True)
    master_class = models.ForeignKey(MasterClass, related_name='payment_masterclass', on_delete=models.CASCADE, null=True, blank=True)
    fio = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    card_number = models.CharField(max_length=16)
    card_expiry = models.DateField()
    card_cvv = models.CharField(max_length=3)
    payment_method = models.CharField(max_length=10, choices=[('visa', 'Visa'), ('mastercard', 'MasterCard')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.course} - {self.tariff} - {self.master_class} - {self.fio}'

class Feedback(models.Model):
    user = models.ForeignKey(UserProfile, related_name='feedbacks', on_delete=models.CASCADE)
    course = models.ForeignKey(Cours, related_name='feedbacks_course', on_delete=models.CASCADE)
    statya = models.ForeignKey(Statya, related_name='statya_feedback', on_delete=models.CASCADE)
    master_class = models.ForeignKey(MasterClass, related_name='master_class_feedback', on_delete=models.CASCADE)
    text = models.TextField()
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.course}'

class Comment(models.Model):
    user = models.ForeignKey(UserProfile, related_name='comments', on_delete=models.CASCADE)
    course = models.ForeignKey(Cours, related_name='comment_course', on_delete=models.CASCADE)
    statya = models.ForeignKey(Statya, related_name='statya_comment', on_delete=models.CASCADE)
    master_class = models.ForeignKey(MasterClass, related_name='master_class_comment', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', related_name='relies', null=True, blank=True, on_delete=models.CASCADE)
    text = models.TextField()
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.course}'



