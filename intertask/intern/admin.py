from django.contrib import admin
from .models import Country, State, City, Employee, TaskDetails, TaskScreenshot, Taskassigning, CustomUser
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)
    list_per_page = 7

admin.site.index_title="Employee Management System"
admin.site.site_header="Employee Management Dashboard"
admin.site.site_title ="Employee Management"


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ("name", "country_name")
    search_fields = ("name", "country__name")
    list_filter = ("country__name",)
    ordering = ("country__name", "name")
    list_per_page = 7
    

    def country_name(self, obj):
        return obj.country.name.upper()
    country_name.short_description = "Country"




@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "state_name", "country_name")
    search_fields = ("name", "state__name", "state__country__name")
    list_filter = ("state__country", "state")
    ordering = ("state__country__name", "state__name", "name")
    list_per_page = 7
    

    def state_name(self, obj):
        return obj.state.name
    state_name.short_description = "State"

    def country_name(self, obj):
        return obj.state.country.name
    country_name.short_description = "Country"

# Inline for TaskScreenshot
class TaskScreenshotInline(admin.TabularInline):
    model = TaskScreenshot
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return "-"
    preview.short_description = "Preview"


@admin.register(TaskDetails)
class TaskDetailsAdmin(admin.ModelAdmin):
    list_display = ("title", "employee", "status", "priority", "date", "estimated_hours")
    list_filter = ( "employee__full_name","employee__role","status", "priority", "date")
    search_fields = ("title", "employee__full_name")
    ordering = ("-date",)
    inlines = [TaskScreenshotInline]
    readonly_fields = ("estimated_hours",)
    raw_id_fields = ['employee']

    fieldsets = (
        ("Task Info", {"fields": ("employee", "title", "description", "task_type")}),
        ("Links", {"fields": ("git_link", "hosting_link")}),
        ("Timing & Status", {"fields": ("date", "start_time", "end_time", "status", "priority", "estimated_hours")}),
    )
    list_per_page = 10


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'role', 'phone', 'email', 'job_title', 'joining_date')
    search_fields = ('full_name', 'phone', 'email', 'aadhaar_number', 'bank_account')
    list_filter = ('role', 'gender', 'marital_status', 'job_title')
    readonly_fields = ('created_on', 'updated_on')
    list_editable = ['phone','email','job_title']
    list_per_page = 10



# Register CustomUser
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'is_staff', 'is_active', 'employee')
    list_filter = ('is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'first_name', 'last_name', 'employee')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active', 'employee')}
        ),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)
    list_per_page = 10

admin.site.register(CustomUser, CustomUserAdmin)



@admin.register(Taskassigning)
class TaskassigningAdmin(admin.ModelAdmin):
    list_display = ("title", "employee", "priority" ,"assigned_at")
    raw_id_fields = ('employee',)
    list_filter = ("employee__role", "employee__full_name","assigned_at", "priority")
    search_fields = ("title", "employee__full_name")
    ordering = ("-assigned_at",)
    list_per_page = 10

