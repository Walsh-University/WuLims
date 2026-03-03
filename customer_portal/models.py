# This will have a bridge to existing customers and person models.
from django.db import models

from customers.models import Customer


# This will be something to enforce tenant boundaries
class CustomerMembership(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.customer.customer_name)


# This is how customers will "initiate" a project.
class ProjectRequest(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.customer.customer_name)
