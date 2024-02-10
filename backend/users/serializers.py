from djoser.serializers import UserSerializer
from rest_framework import serializers, validators

from api import serializers as apiserializers
from users.models import CustomUser, Subscription


class CustomUserSerializer(UserSerializer):
    '''Сериализатор кастомного пользователя.'''
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj).exists()


# class CustomUserCreateSerializer(UserCreateSerializer):
#    '''Сериализатор создания пользователя. Не используется в проекте.'''
#    class Meta:
#       model = CustomUser
#       fields = ('email', 'password', 'username', 'first_name', 'last_name')


class SubscriptionSerializer(serializers.ModelSerializer):
    '''Сериализатор для получения списка подписок.'''
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed',
            'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (Subscription.objects.filter(
            user=request.user, author=obj).exists()
            and request.user.is_authenticated)

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit', False)
        if recipes_limit:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        return apiserializers.RecipeSerializer(
            recipes, many=True, context={'request': request}
        ).data


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    '''Сериализатор для создания подписки.'''
    class Meta:
        model = Subscription
        fields = ('user', 'author')
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=['user', 'author'],
                message='Вы уже подписаны на этого автора'
            )
        ]

    def validate(self, attrs):
        if attrs.get('user') == attrs.get('author'):
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        return attrs

    def to_representation(self, instance):
        request = self.context.get('request')
        return SubscriptionSerializer(
            instance.author,
            context={'request': request}
        ).data
