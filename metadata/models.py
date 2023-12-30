from django.db import models

# Create your models here.

class TextSubmission(models.Model):
    text_content = models.TextField()
