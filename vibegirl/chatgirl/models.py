from django.db import models

# Create your models here.
class ChatHistory(models.Model):
    user_input = models.TextField()
    bot_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_input[:30]} → {self.bot_response[:30]}"
