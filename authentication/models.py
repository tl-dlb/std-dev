from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy
from django.contrib.auth.signals import user_logged_in, user_logged_out

from django.utils import timezone
from company.models import Company


class Profile(models.Model):
    user      = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=gettext_lazy('Пользователь'))
    idn       = models.CharField(default='', max_length=12,  verbose_name='ИИН')
    signature = models.CharField(max_length=1024, verbose_name=gettext_lazy('ЭЦП'), default='')

    company = models.ForeignKey(Company, on_delete=models.RESTRICT,null=True,blank=True, verbose_name=gettext_lazy('Компания'), related_name='users', )

    class Meta:
        verbose_name = gettext_lazy('Профиль')
        verbose_name_plural = gettext_lazy('Профили')

    def __str__(self):
        return '%s' % (self.user.username)


class UserLoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True, verbose_name=gettext_lazy('Вход'))
    logout_time = models.DateTimeField(null=True, blank=True, verbose_name=gettext_lazy('Выход'))
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=gettext_lazy('Компания'))
    def __str__(self):
        return f'{self.user.username} - {self.login_time}'

@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    company = user.profile.company if hasattr(user, 'profile') else None
    UserLoginHistory.objects.create(user=user, login_time=timezone.now(), company=company)

@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    user_history = UserLoginHistory.objects.filter(user=user, logout_time__isnull=True).latest('login_time')
    user_history.logout_time = timezone.now()
    user_history.save()
