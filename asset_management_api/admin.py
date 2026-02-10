from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import SignupUser


class SignupUserAdmin(UserAdmin):
    model = SignupUser

    list_display = ('username', 'email', 'phone', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone',)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('phone',)}),
    )

    search_fields = ('username', 'email', 'phone')
    ordering = ('username',)


admin.site.register(SignupUser, SignupUserAdmin)

# admin.site.register(Asset)
# admin.site.register(ProductionLine)
# admin.site.register(Process)
# admin.site.register(Client)

