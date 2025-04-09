from django.db import models
from django.utils.translation import gettext_lazy as _

class StatusChoices:
    """Константы для статусов"""
    NEW = 'new'
    PROCESSED = 'processed'
    REJECTED = 'rejected'
    PENDING = 'pending'
    APPROVED = 'approved'

    APPEAL_STATUSES = [
        (NEW, _('Новое')),
        (PROCESSED, _('Обработано')),
        (REJECTED, _('Отклонено')),
    ]

    ADMIN_REQUEST_STATUSES = [
        (PENDING, _('В ожидании')),
        (APPROVED, _('Одобрено')),
        (REJECTED, _('Отклонено')),
    ]


class User(models.Model):
    """
    Модель пользователя.
    """
    telegram_id = models.BigIntegerField(unique=True, verbose_name=_('Telegram ID'))
    username = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Имя пользователя'))
    first_name = models.CharField(max_length=255, default="", verbose_name=_('Имя'))
    last_name = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Фамилия'))
    is_admin = models.BooleanField(default=False, verbose_name=_('Администратор'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
        ordering = ['-created_at']

    def __str__(self):
        return self.username or f"{self.first_name} {self.last_name}"


class CommissionInfo(models.Model):
    """
    Модель комиссии.
    """
    name = models.CharField(max_length=255, unique=True, verbose_name=_('Название'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Описание'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))

    class Meta:
        verbose_name = _('Комиссия')
        verbose_name_plural = _('Комиссии')
        ordering = ['name']

    def __str__(self):
        return self.name


class Appeal(models.Model):
    """
    Модель обращения.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='appeals',
        verbose_name=_('Пользователь')
    )
    commission = models.ForeignKey(
        CommissionInfo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appeals',
        verbose_name=_('Комиссия')
    )
    appeal_text = models.TextField(verbose_name=_('Текст обращения'))
    contact_info = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('Контактная информация')
    )
    file_path = models.FileField(
        upload_to='uploads/',
        null=True,
        blank=True,
        verbose_name=_('Прикрепленный файл')
    )
    status = models.CharField(
        max_length=50,
        choices=StatusChoices.APPEAL_STATUSES,
        default=StatusChoices.NEW,
        verbose_name=_('Статус'),
        help_text=_('Возможные статусы: Новое, Обработано, Отклонено.')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))

    class Meta:
        verbose_name = _('Обращение')
        verbose_name_plural = _('Обращения')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Обращение #{self.id} ({self.get_status_display()})"


class Notification(models.Model):
    """
    Модель уведомлений.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Пользователь')
    )
    appeal = models.ForeignKey(
        Appeal,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name=_('Обращение')
    )
    message = models.TextField(
        verbose_name=_('Сообщение'),
        help_text=_('Текст уведомления, который будет отправлен пользователю.')
    )
    sent = models.BooleanField(default=False, verbose_name=_('Отправлено'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))

    class Meta:
        verbose_name = _('Уведомление')
        verbose_name_plural = _('Уведомления')
        ordering = ['-created_at']

    def __str__(self):
        return f"Уведомление #{self.id}: {self.message[:50]}..."


class AdminRequest(models.Model):
    """
    Модель запроса на администрирование.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='admin_requests',
        verbose_name=_('Пользователь')
    )
    admin_position = models.CharField(
        max_length=255,
        verbose_name=_('Должность'),
        help_text=_('Желаемая должность администратора.')
    )
    status = models.CharField(
        max_length=50,
        choices=StatusChoices.ADMIN_REQUEST_STATUSES,
        default=StatusChoices.PENDING,
        verbose_name=_('Статус'),
        help_text=_('Возможные статусы: В ожидании, Одобрено, Отклонено.')
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Комментарий'),
        help_text=_('Комментарий администратора при отклонении.')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))

    class Meta:
        verbose_name = _('Запрос администратору')
        verbose_name_plural = _('Запросы администраторам')
        ordering = ['-created_at']

    def __str__(self):
        return f"Запрос #{self.id} от {self.user} ({self.get_status_display()})"
