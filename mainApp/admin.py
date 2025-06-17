from django.contrib import admin
from .models import  Product, Order, Category,CartItem, Cart,UserProfile
from django.utils.translation import gettext_lazy as _
# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category', 'created_at')
    search_fields = ('name', 'category__name')
    list_filter = ('category',)
    ordering = ('-created_at',)
class OrderAdmin(admin.ModelAdmin):
    search_fields = ('user__username',)
    ordering = ('-created_at',)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)
class Cart1Admin(admin.ModelAdmin):
    
    ordering = ('-created_at',)

admin.site.register(UserProfile)
admin.site.register(CartItem)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Cart, Cart1Admin)





admin.site.site_header = "Elite Admin"
admin.site.site_title = "Elite Admin Portal"
admin.site.index_title = "Welcome to Elite Admin Portal"
admin