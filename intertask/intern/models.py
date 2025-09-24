from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from datetime import datetime, timedelta
from django.contrib.auth.models import AbstractUser

class Country(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'country'

class State(models.Model):
    name = models.CharField(max_length=50, unique=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="states")

    def __str__(self):
        return f"{self.name}, {self.country.name}"
    
    class Meta:
        db_table = 'state'

class City(models.Model):
    name = models.CharField(max_length=50, unique=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="cities")

    def __str__(self):
        return f"{self.name}, {self.state.name}"
    
    class Meta:
        db_table = 'city'


# Employee details
class Employee(models.Model):
    ROLE_CHOICES = [
        ("EMPLOYEE", "Employee"),
        ("INTERN", "Intern"),
    ]

    GENDER_CHOICES = [
        ("MALE", "Male"),
        ("FEMALE", "Female"),
        ("OTHER", "Other"),
    ]

    MARITAL_STATUS_CHOICES = [
        ("SINGLE", "Single"),
        ("MARRIED", "Married"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    full_name = models.CharField(max_length=255)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    address = models.TextField()
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES)
    job_title = models.CharField(max_length=255)
    joining_date = models.DateField()
    pan_number = models.CharField(max_length=20, null=True, blank=True)
    aadhaar_number = models.CharField(max_length=20, unique=True)
    bank_account = models.CharField(max_length=50, unique=True)
    ifsc_code = models.CharField(max_length=20, null=True, blank=True)
    pf_number = models.CharField(max_length=30, null=True, blank=True)
    previous_company = models.CharField(max_length=255, null=True, blank=True)
    experience_years = models.DecimalField(max_digits=4, decimal_places=1, default=0.0, null=True, blank=True)
    experience_certificate = models.FileField( upload_to="experience_certificates/",null=True,blank=True,validators=[FileExtensionValidator(allowed_extensions=["pdf"])])
    college_name = models.CharField(max_length=255)
    course = models.CharField(max_length=100)
    year_of_pass = models.IntegerField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name


    class Meta:
        db_table = "employee"


class CustomUser(AbstractUser):

    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name="user_account", null=True, blank=True)

    def __str__(self):
        return self.username


# Intern or emmpoyee Task Details
class TaskDetails(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    date = models.DateField()
    description = models.TextField()
    git_link = models.URLField(max_length=500, blank=True, null=True)        
    hosting_link = models.URLField(max_length=500, blank=True, null=True)    
    task_type = models.CharField(max_length=100, blank=True, null=True)  
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=50,choices=[("Pending", "Pending"),("In Progress", "In Progress"),("Completed", "Completed"),("Blocked", "Blocked"),],default="Pending")
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    priority = models.CharField(max_length=20,choices=[("Low", "Low"),("Medium", "Medium"),("High", "High"),],default="Medium")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.start_time and self.end_time:
            start_dt = datetime.combine(self.date, self.start_time)
            end_dt = datetime.combine(self.date, self.end_time)

            if end_dt < start_dt:
                end_dt += timedelta(days=1)

            duration = end_dt - start_dt
            hours = duration.total_seconds() / 3600  
            self.estimated_hours = round(hours, 2)

        super().save(*args, **kwargs)

    class Meta:
        db_table = "task_details"

    def __str__(self):
        return f"{self.title} - {self.employee.full_name}"


class TaskScreenshot(models.Model):
    task = models.ForeignKey(TaskDetails, on_delete=models.CASCADE, related_name="screenshots")
    image = models.ImageField(upload_to="task_screenshots/")

    class Meta:
        db_table = "task_image"

    def __str__(self):
        return f"Screenshot for {self.task.title}"
    
class Taskassigning(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="assigned_tasks")
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=20,choices=[("Low", "Low"),("Medium", "Medium"),("High", "High"),],default="Medium")
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "task_assigning"

    def __str__(self):
        return f"{self.title} assigned to {self.employee.full_name}"