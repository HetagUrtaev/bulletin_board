from django.urls import path, include
from . import views
from .views import (AdDetail, AdList, ResponseList,
                    acceptance_response, refusal_response,
                    MyDetail, ad_delete, AdEdit)

app_name = 'board'

urlpatterns = [
# главная страницы
    path('',
         views.AdListView.as_view(),
         name='main_list'),

# страница регистрации
    path('register/',
         views.register_view,
         name='register'),

# страница для подтверждения одноразового пароля, при регистрации
    path('confirm_code/<int:user_id>/',
         views.confirm_code_view,
         name='confirm_code'),

# страница входа пользователя
    path('login/', views.custom_login_view, name='login'),

# пакет allauth
    path('accounts/',
         include('allauth.urls')),

# страница создания публикации
    path("ad/create",
         views.AdCreate.as_view(),
         name='ad_create'),

# страница все публикации
    path('ad/list',
         AdList.as_view(),
         name='ad_list'),

# страница конкретной публикации
    path('ad/<int:pk>/',
         AdDetail.as_view(),
         name='ad_detail'),

# страница "Мои отклики"
    path('response/list',
         ResponseList.as_view(),
         name='response_list'),

# кнопка для принятия отклика
    path('acceptance/<int:pk>/', acceptance_response, name='acceptance_response'),

# кнопка для отклонения отклика
    path('refusal/<int:pk>/', refusal_response, name='refusal_response'),

# страница для просмотра конкретного объявления пользователя
    path('my-ads/<int:pk>/',
         MyDetail.as_view(),
         name='my_detail'),

# кнопка для удаления объявления
    path('ad_delete/<int:pk>/', ad_delete, name='ad_delete'),

# страница для редактирования публикации
    path('ad_edit/<int:pk>/',  AdEdit.as_view(), name='ad_edit'),
]



