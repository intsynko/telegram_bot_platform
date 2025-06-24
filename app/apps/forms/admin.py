from django.contrib import admin
from .models import Form, FormField, FieldValidation

class FieldValidationInline(admin.TabularInline):
    model = FieldValidation
    extra = 1

class FormFieldInline(admin.TabularInline):
    model = FormField
    extra = 1

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    inlines = [FormFieldInline]
    list_display = ('id', 'name')

@admin.register(FormField)
class FormFieldAdmin(admin.ModelAdmin):
    inlines = [FieldValidationInline]
    list_display = ('id', 'name', 'form', 'field_type', 'required')
    list_filter = ('form', 'field_type', 'required')

@admin.register(FieldValidation)
class FieldValidationAdmin(admin.ModelAdmin):
    list_display = ('id', 'field', 'validation_type', 'value')
    list_filter = ('validation_type', 'field')
