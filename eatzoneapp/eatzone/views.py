from rest_framework import generics, viewsets, parsers, permissions, status
from rest_framework.decorators import action
from rest_framework.views import Response
from .models import Category, Store, User, Dish, Tag, Comment, Like, Rating
from .perms import CommentOwner
from .serializers import CategorySerializer, StoreSerializer, DishSerializer, UserSerializer, DishDetailsSerializer, \
    AuthorizedDishDetailsSerializer, CommentSerializer


class CategoryViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class StoreViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Store.objects.filter(active=True)
    serializer_class = StoreSerializer

    def get_queryset(self):
        q = self.queryset

        kw = self.request.query_params.get('kw')
        if kw:
            q = q.filter(name__icontains=kw)

        cate_id = self.request.query_params.get('cate_id')
        if cate_id:
            q = q.filter(category_id=cate_id)

        return q

    @action(methods=['get'], detail=True, url_path='dishs')
    def dishs(self, request, pk):
        store = self.get_object()
        dishs = store.dishs.filter(active=True)

        kws = request.query_params.get('kws')
        if kws:
            dishs = dishs.filter(name__icontains=kws)

        return Response(DishSerializer(dishs, many=True).data)


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    parser_classes = [parsers.MultiPartParser, ]

    def get_permissions(self):
        if self.action in ['current_user']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=['get', 'put'], detail=False, url_path='current-user')
    def current_user(self, request):
        u = request.user
        if request.method.__eq__('PUT'):
            for k, v in request.data.items():
                setattr(u, k, v)
            u.save()

        return Response(UserSerializer(u, context={'request': request}).data)


class DishViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = Dish.objects.filter(active=True)
    serializer_class = DishDetailsSerializer

    def get_permissions(self):
        if self.action in ['assign_tags', 'comments', 'like', 'rating']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            return AuthorizedDishDetailsSerializer

        return self.serializer_class

    @action(methods=['post'], detail=True, url_path='tags')
    def assign_tags(self, request, pk):
        dish = self.get_object()
        tags = request.data['tags']
        for t in tags:
            tag, _ = Tag.objects.get_or_create(name=t)
            dish.tags.add(tag)
        dish.save()

        return Response(DishDetailsSerializer(dish, context={'request': request}).data)

    @action(methods=['post'], detail=True, url_path='comments')
    def comments(self, request, pk):
        c = Comment(content=request.data['content'], dish=self.get_object(), user=request.user)
        c.save()

        return Response(CommentSerializer(c).data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=True, url_path='like')
    def like(self, request, pk):
        l, created = Like.objects.get_or_create(dish=self.get_object(), user=request.user)
        if not created:
            l.liked = not l.liked
        l.save()

        return Response(status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='rating')
    def rating(self, request, pk):
        r, _ = Rating.objects.get_or_create(dish=self.get_object(), user=request.user)
        r.rate = request.data['rate']
        r.save()

        return Response(status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ViewSet, generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = Comment.objects.filter(active=True)
    serializer_class = CommentSerializer
    permission_classes = [CommentOwner, ]

