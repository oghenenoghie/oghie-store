from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .models import UserProfile


admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name')


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    search_fields = ('name',)


@admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    list_display = ('user', 'role', 'company_name', 'phone', 'is_active', 'created_at')
    list_filter = ('role', 'is_active')
    search_fields = ('user__username', 'user__email', 'company_name', 'phone')
    readonly_fields = ('created_at', 'updated_at')
