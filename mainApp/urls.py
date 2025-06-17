from django.urls import path, include
from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    CategoryViewSet,
    ProductViewSet,
    CartViewSet,
    UserProfileViewSet,
    RegisterAPIViewSet
)


router = DefaultRouter()
router.register(r'categories', CategoryViewSet,basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'carts', CartViewSet, basename='cart')


urlpatterns = [
   path('register', RegisterAPIViewSet.as_view(), name='register'),
    path('user-profile/', UserProfileViewSet.as_view(), name='user-profile'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('', include(router.urls)),
]