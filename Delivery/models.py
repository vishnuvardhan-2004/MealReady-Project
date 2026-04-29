from django.db import models

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=50)
    username = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=20)
    mobile = models.CharField(max_length=15)
    address = models.CharField(max_length=100)

class Restaurant(models.Model):
    name = models.CharField(max_length=50)
    picture = models.URLField(max_length = 200, default='https://images.travelandleisureasia.com/wp-content/uploads/sites/2/2025/05/02141004/aesthetic-rest-hero.jpeg?tr=w-1200,q-60')
    cuisine = models.CharField(max_length = 200)
    rating = models.FloatField()
    location = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)

class Item(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="items"
    )
    name = models.CharField(max_length=50)
    description = models.TextField()
    price = models.FloatField()

    vegetarian = models.BooleanField(default=False)

    non_vegetarian = models.BooleanField(default=False)
    soup = models.BooleanField(default=False)
    other = models.BooleanField(default=False)

    picture = models.URLField(
        max_length=200,
        default='https://www.pngall.com/wp-content/uploads/5/Food-Item-PNG-High-Quality-Image.png'
    )

class Cart(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)

    def total_price(self):
        return sum(item.total_price() for item in self.cart_items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="cart_items"
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.item.price * self.quantity