from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly
                                        )
from rest_framework.response import Response

from api.pagination import CustomPagination
from users.models import CustomUser, Subscription
from users.serializers import (CustomUserSerializer,
                               SubscriptionCreateSerializer,
                               SubscriptionSerializer)


class CustomUserViewSet(UserViewSet):
    '''Вьюсет для кастомного юзера.'''
    queryset = CustomUser.objects.select_related('auth_token').all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPagination

    @action(detail=False,
            methods=['GET'],
            permission_classes=[IsAuthenticated]
            )
    def subscriptions(self, request):
        subscriptions = CustomUser.objects.filter(
            following__user=request.user
        )
        pages = self.paginate_queryset(subscriptions)
        serializer = SubscriptionSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=['POST', 'DELETE'],
            url_path='subscribe',
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(CustomUser, pk=id)
        if request.method == 'POST':
            serializer = SubscriptionCreateSerializer(
                data={'user': user.id,
                      'author': author.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            get_object_or_404(
                Subscription, user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
