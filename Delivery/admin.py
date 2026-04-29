from django.contrib import admin

from .models import Cart, User, Restaurant, Item, CartItem

# Register your models here.
admin.site.register(User)
admin.site.register(Restaurant)
admin.site.register(Item)
admin.site.register(Cart)
admin.site.register(CartItem)