from django.contrib.auth.models import User
from rest_framework import viewsets, permissions
from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from rest_framework.decorators import action

from .models import (
    Category,
    Product,
    Cart,
    CartItem,
    Order,
    OrderItem,

)

from .serializers import (
    CategorySerializer,
    ProductSerializer,
    CartSerializer,
    CartItemSerializer,
    OrderSerializer,
    OrderItemSerializer,
    UserProfileSerializer,
    RegisterAPI,
)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]  # Allow any user to view products

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__name=category)
        return queryset

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Cart, CartItem, Product, Order, OrderItem
from .serializers import CartSerializer, OrderSerializer
import stripe
from django.conf import settings
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class CartViewSet(viewsets.ViewSet):
    #stripe.api_key = settings.STRIPE_SECRET_KEY
    def get_cart(self, request):
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
        else:
            session_key = request.session.session_key or request.session.save() or request.session.session_key
            cart, _ = Cart.objects.get_or_create(session_key=session_key)
        return cart

    def list(self, request):
        cart = self.get_cart(request)
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['post'])
    def decrement_item(self, request):
        product_id = request.data.get('product_id')
        cart = self.get_cart(request)
        product = Product.objects.get(id=product_id)
        try:
            item = cart.items.get(product_id=product_id)
            if item.quantity > 1:
                item.quantity -= 1
                product.stock += 1
                product.save()
                item.save()
                return Response({'status': 'quantity decreased'})
            else:
                item.delete()
                return Response({'status': 'item removed'})
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found in cart'}, status=404)


    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        product_id = request.data.get('product_id')
        cart = self.get_cart(request)
        product = Product.objects.get(id=product_id)
        try:
            item = cart.items.get(product_id=product_id)
            product.stock += item.quantity
            product.save()
            item.delete()
            return Response({'status': 'item removed'})
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        product = Product.objects.get(id=request.data['product_id'])
        quantity = int(request.data.get('quantity', 1))
        cart = self.get_cart(request)
        
        print(product.stock)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += quantity   
        else:
            item.quantity = quantity
            
            print(product.stock)

        if product.stock == 0:
            return Response({'status': 'out of stock'})
        product.stock -= quantity
        product.save()
        item.save()
        return Response({'status': 'item added'})
    

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def checkout(self, request):
        cart = self.get_cart(request)
        cart_items = cart.items.select_related('product')

        if not cart_items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        total = sum(item.product.price * item.quantity for item in cart_items)

        order = Order.objects.create(user=request.user, total=total)

        order_items = [
            OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            ) for item in cart_items
        ]
        OrderItem.objects.bulk_create(order_items)

        cart_items.delete()

        return Response(OrderSerializer(order).data)


class UserProfileViewSet(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self,request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
class RegisterAPIViewSet(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterAPI
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        headers = self.get_success_headers(serializer.data)
        return Response({'refresh':str(refresh),'access':str(refresh.access_token)}, status=status.HTTP_201_CREATED, headers=headers)



'''

class CartViewSet(CreateModelMixin,GenericViewSet):
   queryset = Cart.objects.all()
   serializer_class = CartSerializer
   permission_classes = [permissions.AllowAny]


"""
    def get_cart(self):
        user = self.request.user
        if user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=user)
        else:
            session_key = self.request.session.session_key
            if not session_key:
                self.request.session.create()
                session_key = self.request.session.session_key
            cart, _ = Cart.objects.get_or_create(session_key=session_key)
        return cart
"""
            
class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [permissions.AllowAny]

    def get_cart(self):
        user = self.request.user
        if user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=user)
        else:
            session_key = self.request.session.session_key
            if not session_key:
                self.request.session.create()
                session_key = self.request.session.session_key
            cart, _ = Cart.objects.get_or_create(session_key=session_key)
        return cart

    def create(self, request, *args, **kwargs):
        cart = self.get_cart()
        product_id = request.data.get('product')
        quantity = int(request.data.get('quantity', 1))

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product_id=product_id)
       
        if not created:
            cart_item.quantity += quantity
            if cart_item.quantity <= 0:
                cart_item.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            cart_item.save()
            serializer = self.get_serializer(cart_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            if quantity <= 0:
                return Response({'detail': 'Quantity must be greater than zero.'}, status=status.HTTP_400_BAD_REQUEST)
       
            cart_item.quantity = quantity
            cart_item.save()
            serializer = self.get_serializer(cart_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='my-cart')
    def my_cart(self, request):
        cart = self.get_cart()
        items = CartItem.objects.filter(cart=cart)
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)
    
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return orders for the current user
        return Order.objects.filter(user=self.request.user)
    
class UserProfileViewSet(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self,request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
class RegisterAPIViewSet(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterAPI
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        headers = self.get_success_headers(serializer.data)
        return Response({'refresh':str(refresh),'access':str(refresh.access_token)}, status=status.HTTP_201_CREATED, headers=headers)


"""
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def initiate_payment(self, request):
        cart = self.get_cart(request)
        items = cart.items.select_related('product')

        if not items.exists():
            return Response({'error': 'Cart is empty'}, status=400)

        line_items = []
        for item in items:
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': item.product.name,
                    },
                    'unit_amount': int(item.product.price * 100),  # in cents
                },
                'quantity': item.quantity,
            })

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            customer_email=request.user.email,
            success_url='https://your-frontend.com/payment/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://your-frontend.com/payment/cancel',
        )

        return Response({'checkout_url': session.url})"""
'''


