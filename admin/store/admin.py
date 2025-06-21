from django.contrib import admin
from django.utils.html import format_html

from .models import Category, SubCategory, Product, TelegramUser, Order, OrderItem, FAQ, Cart, CartItem


# Inline подкатегории в категории
class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    inlines = [SubCategoryInline]


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category']
    list_filter = ['category']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'subcategory', 'image_preview']
    list_filter = ['subcategory']
    search_fields = ['name', 'description']

    def image_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="60" height="60" />', obj.photo.url)
        return "-"
    image_preview.short_description = "Изображение"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'name', 'address', 'phone', 'is_paid', 'created_at']
    search_fields = ['name', 'phone']
    list_filter = ['is_paid', 'created_at']
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity']
    search_fields = ['product__name']


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'first_name', 'last_name', 'created_at']
    search_fields = ['username', 'first_name', 'last_name']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity']
    list_filter = ['cart']
    search_fields = ['product__name']