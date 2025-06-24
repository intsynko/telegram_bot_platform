from django.contrib import admin
from apps.menu.models import Menu, MenuField


class MenuFieldInline(admin.TabularInline):
    model = MenuField
    extra = 1

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    inlines = [MenuFieldInline]
    list_display = ('id', 'name')

@admin.register(MenuField)
class FormFieldAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'menu', 'field_type')
    list_filter = ('menu', 'field_type')
