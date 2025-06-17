from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Category,
    Product,
    Cart,
    CartItem,
    Order,
    OrderItem,
    
)
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'




class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Product
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['category'] = CategorySerializer(instance.category).data
        return representation

    def create(self, validated_data):
        category_name = validated_data.pop('category_name', None)
        if category_name:
            category = Category.objects.get(name=category_name)
            validated_data['category'] = category
        return super().create(validated_data)

    def update(self, instance, validated_data):
        category_name = validated_data.pop('category_name', None)
        if category_name:
            category = Category.objects.get(name=category_name)
            validated_data['category'] = category
        return super().update(instance, validated_data)


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = ['id', 'items']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'total', 'created_at', 'items']



class UserProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email','is_staff','first_name','last_name']
#class UserProfileDetailSerializer(serializers.ModelSerializer):

class RegisterAPI(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username','email','password','first_name','last_name')
        def create(self, validated_data):
            user = User(
                username=validated_data['username'],
                email=validated_data['email']
            )
            user.set_password(validated_data['password'])
            user.save()
            return user
