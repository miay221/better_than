from django.db import models

class Feedback(models.Model):
    feedback_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.feedback_text[:50]
