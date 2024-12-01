from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone  # Add the timezone import

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}"

class Support(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}"

class Request(models.Model):  # Renamed 'Rqst' to 'Request' for clarity
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
    ]

    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    text = models.TextField()
    file = models.FileField(upload_to="uploads/", blank=True)  # Removed null=True

    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',  # Default status
    )

    def __str__(self):
        return f"Request by {self.user.user.username}"

    def mark_resolved(self):
        """Mark the request as resolved by updating the status and setting resolved_at."""
        self.status = 'RESOLVED'
        self.resolved_at = timezone.now()  # Ensure timezone is imported
        self.save()

    def start_progress(self):
        """Mark the request as in progress."""
        self.status = 'IN_PROGRESS'
        self.save()
