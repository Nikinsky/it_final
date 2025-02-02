from tkinter.font import names

from django.urls import path, include

from .views import *
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'statya', StatyaViewSet, basename='statya')
router.register(r'master_class', MasterClasslView, basename='master_class')
router.register(r'courses', CourseViewSet, basename='course')

urlpatterns = [
    path('', include(router.urls)),

    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    path('user/', UserProfileListteyView.as_view(), name='user-profile-list'),
    path('user/<int:pk>', UserProfileView.as_view(), name='user-profile-detail'),

    path('about_us/', AboutUSListView.as_view(), name='about_us-list'),
    path('about_school/', AboutSchoolListView.as_view(), name='about_School-list'),

    path('statya_list/', StatyaListView.as_view(), name='statya-list'),

    path('course_list/', CoursListView.as_view(), name='cours-list'),

    path('masterclass_list/', MasterClassListView.as_view(), name='masterclass-list'),

    path('feedback_create/', FeedBackCreateView.as_view(), name='feedback-create'),

    path('feedback_list/', FeedBackListView.as_view(), name='feedback-list'),

    path('comment_create/', CommentCreateView.as_view(), name='comment-create'),

    path('comment_user_list/', CommentListView.as_view(), name='comment_user-list'),

    path('cart/<int:pk>/', CartViewSet.as_view(), name='cart-detail'),
    path('cart/item/',CartItemViewSet.as_view(), name='cart-item-list'),
    #
    path('visa_cart/', VisaCartListView.as_view(), name='visa_cart-list'),
    path('visa_cart_create/', VisaCartCreateView.as_view(), name='visa_cart-create'),
    path('visa_cart_delete/', VisaCartDeleteView.as_view(), name='visa_cart-delete'),
    path('visa_cart_delete/<int:pk>/', VisaCartRetDeleteView.as_view(), name='visa_cart-ret-delete'),

    path('payment_create/', PaymentCreateView.as_view(), name='payment-create'),
    path('payment_list/', PaymentListView.as_view(), name='payment-list'),

    path('payment_course', PaymentCartCourseView.as_view(), name='course_item'),
    path('payment_tariff', PaymentCartTariffView.as_view(), name='tariff_item'),
    path('payment_master_class', PaymentCartMasterClassView.as_view(), name='payment_master_class-list'),


    path('tariff/', TariffView.as_view(), name='tariff-list'),



    path('user_tariff/', UserTariffListView.as_view(), name='user_tariff-list'),
    path('user_course/', UserCourseListView.as_view(), name='user_course-list')


]