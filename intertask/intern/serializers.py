from rest_framework import serializers
from .models import Country, State, City, Employee,TaskDetails, TaskScreenshot, Taskassigning
from django.contrib.auth import authenticate


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"


class StateSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source="country.name", read_only=True)

    class Meta:
        model = State
        fields = ["id", "name", "country", "country_name"]



class CitySerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source="state.name", read_only=True)
    country_name = serializers.CharField(source="state.country.name", read_only=True)

    class Meta:
        model = City
        fields = ["id", "name", "state", "state_name", "country_name"]



class EmployeeSerializer(serializers.ModelSerializer):
    experience_certificate = serializers.FileField(required=False)
    class Meta:
        model = Employee
        fields = "__all__"
        
    def validate_experience_certificate(self, value):
        if value:
            if not value.name.lower().endswith('.pdf'):
                raise serializers.ValidationError("Only PDF files are allowed.")
        return value



class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid username or password")
        data["user"] = user
        return data
    



class TaskScreenshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskScreenshot
        fields = ["id", "image"]


class TaskDetailsSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)
    screenshots = TaskScreenshotSerializer(many=True, read_only=True)

    class Meta:
        model = TaskDetails
        fields = [
            "id",
            "title",
            "description",
            "date",
            "git_link",
            "hosting_link",
            "task_type",
            "status",
            "priority",
            "start_time",
            "end_time",
            "created_at",
            "estimated_hours",
            "employee", 
            "employee_name",
            "screenshots", 
        ]


class TaskAssignSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)

    class Meta:
        model = Taskassigning
        fields = [
            "id",
            "title",
            "description",
            "priority",
            "assigned_at",
            "employee_name",
            "employee",
        ]



