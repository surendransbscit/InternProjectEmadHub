from requests import request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import BasePermission,SAFE_METHODS,IsAuthenticated,AllowAny
from django.shortcuts import get_object_or_404
from rest_framework import generics
from .models import Country, State, City, Employee, TaskDetails, TaskScreenshot, Taskassigning
from .serializers import (CountrySerializer, StateSerializer,
                           CitySerializer, EmployeeSerializer , 
                           LoginSerializer ,TaskDetailsSerializer, 
                           TaskAssignSerializer)
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from utils.pagination import paginate_queryset
from utils.openai import generate_next_tasks
from knox.models import AuthToken
from rest_framework.authtoken.models import Token
from django.utils import timezone


# Only staff All user only get
class IsStaffOrAuthenticatedReadOnly(BasePermission):

    def has_permission(self, request, view):
        if request.user and request.user.is_staff:
            return True
        
        # Non-staff authenticated users only allow safe methods (GET)
        if request.user and request.user.is_authenticated:
            return request.method in permissions.SAFE_METHODS
        
        return False
    
# user All and staff get
class OnlyforAuthencationusers(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if not request.user.is_staff:
                return True
            return request.method in SAFE_METHODS
        return False

# Only staff user
class IsStaffUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token = AuthToken.objects.create(user)[1]

            response_data = {
                "token": token,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                }
            }

            if user.is_staff:

                response_data["user"]["is_staff"] = True
                response_data["user"]["employee_id"] = None

            else:
                employee_id = None
                if hasattr(user, "employee") and user.employee:
                    employee_id = user.employee.id

                response_data["user"]["is_staff"] = False
                response_data["user"]["employee_id"] = employee_id

            return Response(response_data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# only staff
# Country CRUD
class CountryListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsStaffUser]
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

    def list(self, request):
        queryset = self.get_queryset()
        return paginate_queryset(queryset, request, self.serializer_class)

# only staff
class CountryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStaffUser]
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


# State CRUD
# only staff
class StateListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsStaffUser]
    queryset = State.objects.select_related("country").all()
    serializer_class = StateSerializer

    def list(self, request):
        queryset = self.get_queryset()
        return paginate_queryset(queryset, request, self.serializer_class)


# only staff
class StateRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStaffUser]
    queryset = State.objects.select_related("country").all()
    serializer_class = StateSerializer


# City CRUD
# only staff
class CityListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsStaffUser]
    queryset = City.objects.select_related("state__country").all()
    serializer_class = CitySerializer

    def list(self, request):
        queryset = self.get_queryset()
        return paginate_queryset(queryset, request, self.serializer_class)


# only staff
class CityRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStaffUser]
    queryset = City.objects.select_related("state__country").all()
    serializer_class = CitySerializer
    
# Only staff
class EmployeeList(generics.ListCreateAPIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsStaffUser]
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        queryset = Employee.objects.all()
        request = self.request
        name = request.query_params.get('name', None)
        email = request.query_params.get('email', None)

        if name:
            queryset = queryset.filter(full_name__icontains=name)
        if email:
            queryset = queryset.filter(email__icontains=email)

        return queryset

    def list(self, request):
        queryset = self.get_queryset()
        return paginate_queryset(queryset, request, self.serializer_class)

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# only staff
class EmployeeDetail(APIView):
    permission_classes = [IsStaffUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser] 
    serializer_class = EmployeeSerializer

    def get(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        serializer = EmployeeSerializer(employee, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        serializer = EmployeeSerializer(employee, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        employee.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

# Logout
# together
class UserLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            # Get user token
            token = Token.objects.get(user=request.user)
            token.delete()   # delete token -> logout user
            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({"error": "Token not found"}, status=status.HTTP_400_BAD_REQUEST)



# Only User and staff get
class TaskDetailsListCreateView(generics.ListCreateAPIView):
    queryset = TaskDetails.objects.all().select_related("employee").prefetch_related("screenshots")
    serializer_class = TaskDetailsSerializer
    permission_classes = [OnlyforAuthencationusers]



# Only user and staff get
class TaskDetailsRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TaskDetails.objects.all().select_related("employee").prefetch_related("screenshots")
    serializer_class = TaskDetailsSerializer
    permission_classes = [OnlyforAuthencationusers]

class EmployeeTaskListView(generics.ListAPIView):
    serializer_class = TaskDetailsSerializer
    permission_classes = [OnlyforAuthencationusers]

    def get_queryset(self):
        employee_id = self.kwargs.get("pk")
        return TaskDetails.objects.filter(employee_id=employee_id).select_related("employee").prefetch_related("screenshots")
    

# Only staff 
class TaskNextSuggestionView(APIView):
    permission_classes = [IsStaffUser]

    def get(self, request, pk):

        tasks = (
            TaskDetails.objects.filter(employee_id=pk)
            .select_related("employee")
            .prefetch_related("screenshots")
        )

        serializer = TaskDetailsSerializer(tasks, many=True)
        all_task_data = serializer.data

        ai_suggestions = generate_next_tasks(all_task_data)

        print("aiSuggestions", ai_suggestions)

        tasks_to_create = []
        for block in ai_suggestions.strip().split("\n\n"):
            lines = block.strip().split("\n")
            if len(lines) >= 3:
                title = lines[0].replace("Title:", "").strip()
                description = lines[1].replace("Description:", "").strip()
                priority = lines[2].replace("Priority:", "").strip()
                tasks_to_create.append(
                    Taskassigning(
                        employee_id=pk,
                        title=title,
                        description=description,
                        priority=priority,
                        assigned_at=timezone.now(),
                    )
                )
        print("Tasks to create:", tasks_to_create)

        if tasks_to_create:
            try:
                Taskassigning.objects.bulk_create(tasks_to_create)
            except Exception as e:
                print("Error saving tasks:", e)

        return Response(
            {
                "employee_id": pk,
                "employee_tasks": all_task_data,
                "next_tasks": ai_suggestions,
                # "saved_to_db": len(tasks_to_create),
            },
            status=status.HTTP_200_OK,
        )
    
    
# only staff User Get
# pass employee id based get for assign task
class TaskAssignDetailView(generics.ListAPIView):
    serializer_class = TaskAssignSerializer
    permission_classes = [OnlyforAuthencationusers]

    def get_queryset(self):
        employee_id = self.kwargs.get("pk")
        return Taskassigning.objects.filter(employee_id=employee_id).select_related("employee")
    

class TaskDeleteView(APIView):
    queryset = Taskassigning.objects.all()
    serializer_class = TaskAssignSerializer
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        taskassign = get_object_or_404(Taskassigning, pk=pk)
        taskassign.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    



    
