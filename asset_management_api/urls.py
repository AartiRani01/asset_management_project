# from django.urls import path
# from rest_framework_simplejwt.views import TokenRefreshView
# from .views import (
#     SignupAPI, LoginAPI, LogoutAPI, UserProfileAPI , 
#     AssetListCreateAPI, ProductionLineListCreateAPI, 
#     ProductionLineDetailAPI,ProcessListCreateAPI, 
#     ProcessDetailAPI,
#     ClientListCreateAPI, ClientDetailAPI
# )

# urlpatterns = [
#     # Authentication URLs
#     path('signup/', SignupAPI.as_view(), name='signup'),
#     path('login/', LoginAPI.as_view(), name='login'),
#     path('logout/', LogoutAPI.as_view(), name='logout'),
#     path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
#     path('profile/', UserProfileAPI.as_view(), name='user_profile'),
    
#     # Asset URLs
#     path('assets/', AssetListCreateAPI.as_view(), name='asset_list_create'),
#     # path('assets/<int:pk>/', AssetDetailAPI.as_view(), name='asset_detail'),
    
#     # Production Line URLs
#     path('production-lines/', ProductionLineListCreateAPI.as_view(), name='production_line_list_create'),
#     path('production-lines/<int:pk>/', ProductionLineDetailAPI.as_view(), name='production_line_detail'),
    
#     # Process URLs
#     path('processes/', ProcessListCreateAPI.as_view(), name='process_list_create'),
#     path('processes/<int:pk>/', ProcessDetailAPI.as_view(), name='process_detail'),
    
#     # Client URLs
#     path('clients/', ClientListCreateAPI.as_view(), name='client_list_create'),
#     path('clients/<int:pk>/', ClientDetailAPI.as_view(), name='client_detail'),
# ]


# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from rest_framework_simplejwt.views import TokenRefreshView
# from .views import (
#     SignupAPIViewSet, LoginAPIView, AssetViewSet, 
#     ProductionLineViewSet, ProcessViewSet, ClientViewSet,
#     UserProfileViewSet, LogoutAPIView
# )

# router = DefaultRouter()
# router.register(r'signup', SignupAPIViewSet, basename='signup')
# router.register(r'assets', AssetViewSet, basename='asset')
# router.register(r'production-lines', ProductionLineViewSet, basename='production-line')
# router.register(r'processes', ProcessViewSet, basename='process')
# router.register(r'clients', ClientViewSet, basename='client')
# router.register(r'profile', UserProfileViewSet, basename='profile')

# urlpatterns = [
#     path('', include(router.urls)),
#     path('login/', LoginAPIView.as_view(), name='login'),
#     path('logout/', LogoutAPIView.as_view(), name='logout'),
#     path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
# ]


from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SignupAPIViewSet, ClientViewSet, ProcessViewSet,
    AssetViewSet, ProductionLineViewSet,
    UserProfileViewSet, LoginAPIView, LogoutAPIView,TokenRefreshAPIView
    
)
# from drf_spectacular.views import ( SpectacularAPIView,
#                                   SpectacularRedocView, 
#                                   SpectacularSwaggerView)
# from .views import AlbumViewSet

router = DefaultRouter()

router.register(r'signup', SignupAPIViewSet, basename='signup')
router.register(r'clients', ClientViewSet, basename='clients')
router.register(r'processes', ProcessViewSet, basename='processes')
router.register(r'assets', AssetViewSet, basename='assets')
router.register(r'production-lines', ProductionLineViewSet, basename='production-lines')
router.register(r'profile', UserProfileViewSet, basename='profile')
router.register(r'assets', AssetViewSet, basename='asset')
# router.register(r'albums', AlbumViewSet, basename='album')

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('', include(router.urls)),
    path('token/refresh/', TokenRefreshAPIView.as_view(), name='token_refresh'),

]
