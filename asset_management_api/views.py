from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from .utils import get_location_from_ip ,get_ip
from .models import SignupUser, Asset, ProductionLine, Process, Client
from .serializers import (
    UserSerializer, LoginSerializer, AssetSerializer, 
    ProductionLineSerializer, ProcessSerializer, ClientSerializer
)
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.exceptions import TokenError
from .permissions import GroupBasedPermission
from rest_framework import viewsets
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .models import Asset
from .serializers import (
    AssetSerializer,
    AssetCreateSerializer,
    AssetStatusSerializer
)


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [permissions.IsAuthenticated]

    # CREATE Asset
    @extend_schema(
        request=AssetCreateSerializer,
        responses={201: AssetSerializer},
        description="Create a new asset"
    )
    def create(self, request, *args, **kwargs):
        serializer = AssetCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ip = get_ip(request)
        location_data = get_location_from_ip(ip) or {}

        asset = serializer.save(
            ip_address=location_data.get("ip", ip),
            city=location_data.get("city"),
            region=location_data.get("region"),
            country=location_data.get("country"),
            latitude=location_data.get("latitude"),
            longitude=location_data.get("longitude"),
            created_by=request.user
        )

        return Response(
            AssetSerializer(asset).data,
            status=201
        )

    # LIST Assets
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='name',
                description='Filter assets by name',
                required=False,
                type=str
            ),
            OpenApiParameter(
                name='created_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Filter by created date',
                examples=[
                    OpenApiExample(
                        'Example date',
                        value='2024-01-15'
                    )
                ],
            ),
        ],
        description="Get list of all assets with optional filters"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # CUSTOM ACTION → status
    @extend_schema(
        request=AssetStatusSerializer,
        responses={200: AssetSerializer},
        description="Update asset status"
    )
    @action(detail=True, methods=["post", "get"])
    def set_status(self, request, pk=None):
        asset = self.get_object()

        if request.method == "POST":
            serializer = AssetStatusSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            asset.status = serializer.validated_data["status"]
            asset.save()
            return Response(AssetSerializer(asset).data)

        return Response({
            "id": asset.id,
            "status": asset.status
        })
# -------------------- Signup API --------------------
class SignupAPIViewSet(viewsets.ModelViewSet):
    queryset = SignupUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]



# class SignupAPIViewSet(viewsets.ModelViewSet):
#     queryset = SignupUser.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [permissions.AllowAny]
#     http_method_names = ['post']  # Only allow POST for signup

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()

#         return Response(
#             {
#                 "user": serializer.data,
#                 "message": "User created successfully"
#             },
#             status=status.HTTP_201_CREATED
#         )


# -------------------- Login API --------------------
class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "Login successful",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email if hasattr(user, 'email') else None
                }
            }, status=status.HTTP_200_OK)

        return Response({
            "error": "Invalid username or password"
        }, status=status.HTTP_401_UNAUTHORIZED)


# -------------------- Asset API --------------------
class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [permissions.AllowAny, GroupBasedPermission]
    allowed_groups = ['CEO', 'MANAGER']

    def perform_create(self, serializer):
        ip = get_ip(self.request)
        location_data = get_location_from_ip(ip) or {}

        serializer.save(
            ip_address=location_data.get('ip', ip),
            city=location_data.get('city'),
            region=location_data.get('region'),
            country=location_data.get('country'),
            latitude=location_data.get('latitude'),
            longitude=location_data.get('longitude'),
            created_by=self.request.user
        )


# class AssetViewSet(viewsets.ModelViewSet):
#     queryset = Asset.objects.all()
#     serializer_class = AssetSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def perform_create(self, serializer):
#         ip = get_ip(self.request)
#         location_data = get_location_from_ip(ip) or {}
#         print("location data ",location_data)
#         serializer.save(
#         ip_address=location_data.get('ip', ip),
#         city=location_data.get('city'),
#         region=location_data.get('region'),
#         country=location_data.get('country'),
#         latitude=location_data.get('latitude'),
#         longitude=location_data.get('longitude'),
#         created_by=self.request.user
#     )
        
#     permission_classes = [GroupBasedPermission]
#     allowed_groups = ['CEO']   # only CEO + MANAGER can access

#     def get(self, request):
#         return Response({"msg": "Asset data"})


# -------------------- Production Line API --------------------
class ProductionLineViewSet(viewsets.ModelViewSet):
    queryset = ProductionLine.objects.all()
    print("print this")
    serializer_class = ProductionLineSerializer
    print("print02")
    permission_classes = [permissions.AllowAny, GroupBasedPermission]
    allowed_groups = ['OPERATOR']

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            created_date=timezone.now()
        )

    def perform_update(self, serializer):
        serializer.save(
            created_by=self.request.user,
            created_date=timezone.now()
        )

    @action(detail=True, methods=['get'], url_path='access')
    def access(self, request, pk=None):
        production_line = self.get_object()
        return Response({
            "production_line": production_line.name,
            "status": "Access granted",
            "details": ProductionLineSerializer(production_line).data
        })

# class ProductionLineViewSet(viewsets.ModelViewSet):
#     queryset = ProductionLine.objects.all()
#     serializer_class = ProductionLineSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def perform_create(self, serializer):
#         serializer.save(
#             created_by=self.request.user.username,
#             created_date=timezone.now()
#         )

#     def perform_update(self, serializer):
#         serializer.save(
#             created_by=self.request.user.username,
#             created_date=timezone.now()
#         )

#     @action(detail=True, methods=['get'], url_path='access')
#     def access(self, request, pk=None):

#         production_line = self.get_object()
#         return Response({
#             "production_line": production_line.name,
#             "status": "Access granted",
#             "details": ProductionLineSerializer(production_line).data
#         })


# -------------------- Process API --------------------

class ProcessViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny, GroupBasedPermission]
    allowed_groups = ['OPERATOR']

    queryset = Process.objects.all()
    serializer_class = ProcessSerializer

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            created_date=timezone.now()
        )

    def perform_update(self, serializer):
        serializer.save(
            created_by=self.request.user,
            created_date=timezone.now()
        )
# class ProcessViewSet(viewsets.ModelViewSet):
#     queryset = Process.objects.all()
#     serializer_class = ProcessSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def perform_create(self, serializer):
#         serializer.save(
#             created_by=self.request.user.username,
#             created_date=timezone.now()
#         )

#     def perform_update(self, serializer):
#         serializer.save(
#             created_by=self.request.user.username,
#             created_date=timezone.now()
#         )

#     permission_classes = [GroupBasedPermission]
#     allowed_groups = ['OPERATOR']

#     def get(self, request):
#         return Response({"msg": "Process data"})


# -------------------- Client API --------------------
class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.AllowAny]

    # def perform_create(self, serializer):
    #     ip = get_client_ip(self.request)
    #     location_data = get_location_from_ip(ip)
    #     serializer.validated_data['ip_address']=location_data('ip')

    #     serializer.validated_data['created_by']=self.request.user
    #     serializer.save(
    #             ip_address=location_data.get('ip'),
    #             city=location_data.get('city'),
    #             region=location_data.get('region'),
    #             country=location_data.get('country'),
    #             latitude=location_data.get('latitude'),
    #             longitude=location_data.get('longitude'),
    #             created_by=self.request.user
    #     )

    def perform_create(self, serializer):
        ip = get_ip(self.request)
        location_data = get_location_from_ip(ip) or {}
        print("location data ",location_data)
        serializer.save(
                ip_address=location_data.get('ip', ip),
                city=location_data.get('city'),
                region=location_data.get('region'),
                country=location_data.get('country'),
                latitude=location_data.get('latitude'),
                longitude=location_data.get('longitude'),
                created_by=self.request.user
        )

    # def create(self, request, *args, **kwargs):
    #     try:
    #         return super().create(request, *args, **kwargs)
    #     except Exception as e:
    #         print("Error occurred while saving data:", e)
    #         return Response({"error": "An error occurred while saving data"}, status=status.HTTP_400_BAD_REQUEST)

    # def perform_create(self, serializer):
    #     serializer.save(
    #         created_by=self.request.user,
    #         created_date=timezone.now()
    #     )

    def perform_update(self, serializer):
        serializer.save(
            created_by=self.request.user.username,
            created_date=timezone.now()
        )


# -------------------- User Profile API --------------------
class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['get', 'put', 'patch']  # Only allow retrieve and update

    def get_queryset(self):
        return SignupUser.objects.filter(id=self.request.user.id)

    def get_object(self):
        return self.request.user


# -------------------- Logout API --------------------
class LogoutAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response(
                {"message": "Logout successful"},
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        

#------------------RefreshToken-------------------

class TokenRefreshAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)

            return Response(
                {
                    "message": "Token refreshed successfully",
                    "access": access_token
                },
                status=status.HTTP_200_OK
            )

        except TokenError:
            return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        