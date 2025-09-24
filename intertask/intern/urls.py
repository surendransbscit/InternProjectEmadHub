from django.urls import path
from .views import *

urlpatterns = [

    # Employee Create
    # path('employees/create/', EmployeeCreateAPIView.as_view()),

    # Login
    path("login/", LoginView.as_view()),

    # Logout
    path("logout/", UserLogoutView.as_view()),


    # Employee
    path("employees/", EmployeeList.as_view()),
    path("employees/<int:pk>/", EmployeeDetail.as_view()),

    # Country
    path("countries/", CountryListCreateView.as_view()),
    path("countries/<int:pk>/", CountryRetrieveUpdateDestroyView.as_view()),

    # State
    path("states/", StateListCreateView.as_view()),
    path("states/<int:pk>/", StateRetrieveUpdateDestroyView.as_view()),

    # City
    path("cities/", CityListCreateView.as_view()),
    path("cities/<int:pk>/", CityRetrieveUpdateDestroyView.as_view()),

    # Task Details
    path("tasks/", TaskDetailsListCreateView.as_view()),
    path("tasks/<int:pk>/", TaskDetailsRetrieveUpdateDestroyView.as_view()),

    # Employee Task Details
    path("employees/tasks/<int:pk>/", EmployeeTaskListView.as_view()),

    # AI Suggestions for next tasks
    path("tasks/aisuggestions/<int:pk>/", TaskNextSuggestionView.as_view()),

    # Task Assign Employee
    path("tasks/assign/employee/<int:pk>/", TaskAssignDetailView.as_view()),

    # Task Deleted
    path("assigentask/delete/<int:pk>/", TaskDeleteView.as_view())
    
]
