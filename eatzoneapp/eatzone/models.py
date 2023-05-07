from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField


class User(AbstractUser):
    avatar = models.ImageField(upload_to='users/%Y/%m', null=True)


class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Store(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=100, unique=True)
    description = RichTextField(null=True)
    image = models.ImageField(upload_to='eatzone/%Y/%m', null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    def __str__(self):
        return self.name


class Dish(BaseModel):
    name = models.CharField(max_length=255)
    content = RichTextField()
    price = models.FloatField(null=False)
    image = models.ImageField(upload_to='eatzone/%Y/%m', null=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='dishs')
    tags = models.ManyToManyField('Tag', related_name='dishs')

    def __str__(self):
        return self.name


class Tag(BaseModel):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Comment(BaseModel):
    content = models.CharField(max_length=255)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.content


class ActionBase(BaseModel):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True
        unique_together = ('store', 'user')


class Like(ActionBase):
    liked = models.BooleanField(default=True)


class Rating(ActionBase):
    rate = models.SmallIntegerField(default=0)
