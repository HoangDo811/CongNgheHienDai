from django.contrib import admin
from django import forms
from django.utils.html import mark_safe
from .models import Category, Store, Tag, Dish
from ckeditor_uploader.widgets import CKEditorUploadingWidget


class StoreForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Store
        fields = '__all__'


class DishForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Dish
        fields = '__all__'


class StoreAdmin(admin.ModelAdmin):
    form = StoreForm
    list_display = ["id", "name", "created_date", "active"]
    search_fields = ["name", "id"]
    list_filter = ["name", "category", "created_date"]


class DishTagInlineAdmin(admin.StackedInline):
    model = Dish.tags.through


class DishAdmin(admin.ModelAdmin):
    form = DishForm
    list_display = ["id", "name", "created_date", "store", "active"]
    search_fields = ["name", "id"]
    list_filter = ["name", "store", "created_date", "active"]
    inlines = [DishTagInlineAdmin, ]
    readonly_fields = ['avatar']

    def avatar(self, dish):
        return mark_safe("<img src='/static/{}' width='120' />".format(dish.image.name))

    class Media:
        css = {
            'all': ('/static/css/style.css', )
        }


admin.site.register(Category)
admin.site.register(Store, StoreAdmin)
admin.site.register(Dish, DishAdmin)
admin.site.register(Tag)
