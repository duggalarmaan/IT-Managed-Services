from django.contrib.auth.models import AbstractUser
from django.db import models


# Define a custom user model that extends the built-in AbstractUser model provided by Django
class CustomUser(AbstractUser):
    # Define choices for the user_type field using a tuple of tuples
    USER_TYPE_CHOICES = (
        ('client', 'Client'),
        ('technician', 'Technician'),
        ('admin', 'Admin'),
    )

    # Define a CharField to store the user type, with a maximum length of 20 characters
    # and using the choices defined above
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    performance = models.FloatField(null=True, blank=True)
    # Define a __str__ method that returns the username of the user
    def __str__(self):
        return self.username

    # Define a custom method to get the user type of the user
    def get_user_type(self):
        return self.user_type
    
    def get_average_rating(self):
        # Calculate the average rating based on all tickets worked on by the technician
        tickets = Ticket.objects.filter(assigned=self)
        ratings = [ticket.rating for ticket in tickets if ticket.rating is not None]
        if ratings:
            return sum(ratings) / len(ratings)
        else:
            return 0.0
    

class Service(models.Model):

    service_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.service_name

class Ticket(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('closed', 'Closed'),
    )

    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tickets')
    phone = models.CharField(max_length=20)
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')   
    assigned = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assigned_tickets', null=True, blank=True)
    rating = models.IntegerField(null=True, blank=True)
    rating_description = models.TextField(null=True, blank=True)
    invoice = models.FileField(upload_to='Invoices/', null=True, blank=True)

    # define the string representation of an instance of the model. When you print an instance of the Ticket model, 
    # for example by calling print(ticket_object), it will return the title of the ticket.
    def __str__(self):
        return self.title
    

