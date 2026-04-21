from django.db import models

class Member(models.Model):
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    phone = models.IntegerField(null=True)
    joined_date = models.DateField(null=True)

def __str__(self):
    return f"{self.firstname} {self.lastname}"

class Person:
    def __init__(self,name,age):
        self.nam = name
        self.age = age

    def running(self):
        return f'{self.nam} is running while {self.age} dog followig him at the back' 

p1 = Person('jose', 12)

