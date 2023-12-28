from django.db import models

class Assessment(models.Model):
    audio_file = models.FileField(upload_to='audio_files/')
    transcription = models.TextField()
    suitability_result = models.CharField(max_length=255)

