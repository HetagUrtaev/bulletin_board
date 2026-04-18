from django.views.generic import (TemplateView, ListView,
                                  DetailView, CreateView, UpdateView)
from .filters import ResponseFilter
from .models import Ad, Response
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.models import User
from .models import OneTimeCode
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .forms import AdForm, ResponsesForm
from django.urls import reverse
from django.views.generic.edit import FormMixin
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.contrib import messages


# главная страница
class AdListView(TemplateView):
    template_name = 'main.html'


# Страница добавления публикации
class AdCreate(LoginRequiredMixin, CreateView):
    model = Ad
    form_class = AdForm
    template_name = 'ad_create.html'


    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('board:ad_detail', kwargs={'pk': self.object.pk})


# Просмотр всех публикаций
class AdList(ListView):
    model = Ad
    ordering = '-created_at'
    template_name = 'ad_list.html'
    context_object_name = 'ad_list'
    paginate_by = 20


# Просмотр откликов
class ResponseList(LoginRequiredMixin, ListView):
    model = Response
    ordering = '-created_at'
    template_name = 'response_list.html'
    context_object_name = 'response_list'

    def get_queryset(self):
        queryset = Response.objects.filter(
            ad__author=self.request.user
        ).select_related(
            'author',
            'ad',
            'ad__category'
        )

        self.filterset = ResponseFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filterset = ResponseFilter(
            self.request.GET,
            queryset=self.get_queryset(),
            request=self.request
        )
        filtered_queryset = filterset.qs
        context['filter'] = filterset
        context['response_list'] = filtered_queryset
        context['total_responses'] = filtered_queryset.count()
        return context


# просмотр конкретной публикации и форма для откликов
class AdDetail(LoginRequiredMixin, DetailView, FormMixin): # проверить LoginRequiredMixin
    model = Ad
    template_name = 'ad_detail.html'
    context_object_name = 'ad_detail'
    form_class = ResponsesForm

    def get_success_url(self):
        return reverse('board:ad_detail', kwargs={'pk': self.object.pk})


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form() # добавляем форму в шаблон
        context['responses'] = self.object.responses.all() # получаем все отклики через обратную связь

        return context

    def post(self, request, *args, **kwargs): # DetailView не может обработать форму, поэтому добавляем это явно
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


    def form_valid(self, form):

        if self.object.responses.filter(author=self.request.user).exists():
            form.add_error(None, 'Вы уже оставили отклик на это объявление!')
            return self.form_invalid(form)

        try:

            form.instance.author = self.request.user
            form.instance.ad = self.object
            form.save()

            author_email = self.object.author.email
            if author_email:  # Только если email есть
                send_mail(
                    subject='Новый отклик на вашу публикацию',
                    message=f'На вашу публикацию - {self.object.title} - добавлен новый отклик.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[author_email],
                    fail_silently=False
                )

            return super().form_valid(form)
        except IntegrityError:
            form.add_error(None, 'Ошибка: дублирующий отклик не сохранён (ограничение БД).')
            return self.form_invalid(form)


# просмотр моей публикации с возможностью ее удаления или изменения
class MyDetail(LoginRequiredMixin, DetailView):
    model = Ad
    template_name = 'my_detail.html'
    context_object_name = 'ad'

    def get_queryset(self):
        return super().get_queryset().filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


# кнопка для удаления публикации
@login_required
def ad_delete(request, pk):
    ad = get_object_or_404(Ad, pk=pk, author=request.user)
    ad.delete()
    return redirect('board:response_list')


# страница для изменения публикации
class AdEdit(LoginRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    form_class = AdForm
    model = Ad
    template_name = 'ad_create.html'

    def get_queryset(self): # ограничение для других пользователей
        return Ad.objects.filter(author=self.request.user)

    def get_success_url(self):
        return reverse('board:ad_detail', kwargs={'pk': self.object.pk})


# Страница профиля
class Profile(LoginRequiredMixin, TemplateView):
    template_name = 'account/profile.html'


# Регистрация
def register_view(request):
    if request.method != 'POST':
        return render(request, 'account/register.html')


    username = request.POST.get('username', '')
    email = request.POST.get('email', '')
    password = request.POST.get('password', '')
    password2 = request.POST.get('password2', '')

    error = None

    if password != password2:
        error = 'Пароли не совпадают'

    if not error:
        try:
            existing_user = User.objects.get(username=username)
            if existing_user.is_active:
                error = 'Пользователь с таким именем уже существует'
            else:
                existing_user.email = email
                existing_user.set_password(password)
                existing_user.save()
                user = existing_user
        except User.DoesNotExist:
            try:
                existing_email_user = User.objects.get(email=email)
                if existing_email_user.is_active:
                    error = 'Пользователь с таким email уже существует'
                else:
                    existing_email_user.username = username
                    existing_email_user.set_password(password)
                    existing_email_user.save()
                    user = existing_email_user
            except User.DoesNotExist:
                user = User.objects.create_user(
                    username=username,
            email=email,
            password=password,
            is_active=False
        )

    if error:
        return render(request, 'account/register.html', {
            'error': error,
            'username': username,
            'email': email
        })

    # Удаляем старые коды для этого пользователя (если есть)
    OneTimeCode.objects.filter(user=user).delete()

    # Создаём новый одноразовый код
    otp_code = OneTimeCode.objects.create(user=user)

    # Отправляем код на email
    try:
        send_mail(
            'Код подтверждения регистрации',
            f'Ваш код подтверждения: {otp_code.code}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
    except Exception as e:
        # Если отправка не удалась, удаляем пользователя
        user.delete()
        return HttpResponse(f'Ошибка отправки кода. Попробуйте позже. ({str(e)})')

    return redirect('board:confirm_code', user_id=user.id)


# Проверка одноразового пароля
def confirm_code_view(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return HttpResponse('Пользователь не найден')

    if request.method != 'POST':
        return render(request, 'account/confirm_code.html', {'email': user.email})

    code = request.POST.get('code', '')

    if OneTimeCode.is_code_valid(user, code):
        user.is_active = True
        user.save()
        OneTimeCode.mark_as_used(user, code)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('board:ad_list')
    else:
        return HttpResponse('Неверный или просроченный код')


# Вход пользователя
def custom_login_view(request):


    if request.method == 'POST':
        email = request.POST.get('login')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            if not user.is_active:
                return redirect('board:confirm_code', user_id=user.id)
            else:
                login(request, user)
                return redirect('board:ad_list')
        else:

            messages.error(request, 'Неверные email или пароль')

    return render(request, 'account/login.html')


# кнопка принятия отклика
@login_required
def acceptance_response(request, pk):
    response = Response.objects.get(pk=pk)
    response.status = 'accepted'
    response.save()
    return redirect(request.META['HTTP_REFERER'])


# кнопка отклонения отклика
@login_required
def refusal_response(request, pk):
    response = Response.objects.get(pk=pk)
    response.status = 'rejected'
    response.save()
    return redirect(request.META['HTTP_REFERER'])