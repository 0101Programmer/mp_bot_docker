from django.db import models

class User(models.Model):
    user_id = models.BigIntegerField(primary_key=True)
    username = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.username or str(self.user_id)


class CommissionInfo(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Appeal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    commission = models.ForeignKey(CommissionInfo, on_delete=models.SET_NULL, null=True)
    appeal_text = models.TextField()
    contact_info = models.CharField(max_length=255, null=True, blank=True)
    file_path = models.CharField(max_length=1024, null=True, blank=True)
    status = models.CharField(max_length=255, default='Новая')

    def __str__(self):
        return f"Appeal #{self.id} from {self.user}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    appeal = models.ForeignKey(Appeal, on_delete=models.CASCADE)
    status = models.CharField(max_length=255)
    sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for appeal {self.appeal_id} - {self.status}"