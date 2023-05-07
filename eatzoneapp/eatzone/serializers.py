from rest_framework import serializers
from .models import Category, Store, User, Dish, Tag, Comment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class UserSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(source='avatar')

    def get_image(self, user):
        if user.avatar:
            request = self.context.get('request')
            return request.build_absolute_uri('/static/%s' % user.avatar.name) if request else ''

    def create(self, validated_data):
        data = validated_data.copy()
        u = User(**data)
        u.set_password(u.password)
        u.save()
        return u

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'avatar', 'image']
        extra_kwargs = {
            'avatar': {'write_only': True},
            'password': {'write_only': True}
        }


class StoreSerializer(serializers.ModelSerializer):
    user = UserSerializer
    image = serializers.SerializerMethodField(source='image')

    def get_image(self, store):
        if store.image:
            request = self.context.get('request')
            return request.build_absolute_uri('/static/%s' % store.image.name) if request else ''

    class Meta:
        model = Store
        fields = ['id', 'name', 'address', 'description', 'image', 'created_date', 'user_id', 'category_id']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class DishSerializer(serializers.ModelSerializer):
    # image = serializers.SerializerMethodField(source='image')
    #
    # def get_image(self, dish):
    #     if dish.image:
    #         request = self.context.get('request')
    #         return request.build_absolute_uri('/static/%s' % dish.image.name) if request else ''

    class Meta:
        model = Dish
        fields = ['id', 'name', 'created_date', 'updated_date', 'image']


class DishDetailsSerializer(DishSerializer):
    tags = TagSerializer(many=True)

    class Meta:
        model = DishSerializer.Meta.model
        fields = DishSerializer.Meta.fields + ['content', 'tags']


class AuthorizedDishDetailsSerializer(DishDetailsSerializer):
    liked = serializers.SerializerMethodField()
    rate = serializers.SerializerMethodField()

    def get_liked(self, dish):
        request = self.context.get('request')
        if request:
            return dish.like_set.filter(user=request.user, liked=True).exists()

    def get_rate(self, dish):
        request = self.context.get('request')
        if request:
            r = dish.rating_set.filter(user=request.user).first()
            return r.rate if r else 0

    class Meta:
        model = DishSerializer.Meta.model
        fields = DishSerializer.Meta.fields + ['liked', 'rate']


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Comment
        fields = ["id", "content", "created_date", "user"]
