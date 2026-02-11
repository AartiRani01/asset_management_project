

from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import SignupUser, Asset, ProductionLine, Process, Client
import re
from django.db import models
from django.contrib.auth.models import Group
from .models import Asset


class ClientNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"


class ProcessNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = "__all__"


class UserNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignupUser
        fields = ['id', 'username', 'email', 'phone']


# 1️ Main Asset Serializer (for responses)
class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = '__all__'


# 2️ Asset Create Serializer (for POST request)
class AssetCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ['name', 'description', 'status']  
        # include only fields you want during creation


# 3️ Asset Status Serializer (for custom action set_status)
class AssetStatusSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=50)

    def validate_status(self, value):
        allowed_status = ['active', 'inactive', 'maintenance']
        if value not in allowed_status:
            raise serializers.ValidationError(
                f"Status must be one of {allowed_status}"
            )
        return value


# -------------------- User Serializer --------------------
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    role = serializers.CharField(write_only=True)  # CEO / MANAGER / OPERATOR
    
    class Meta:
        model = SignupUser
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'phone','role']

    def create(self, validated_data):
        role = validated_data.pop('role')

        user = SignupUser.objects.create_user(
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email'),
            phone=validated_data.get('phone'),

        )

        # Assign group (role)
        group = Group.objects.get(name=role)
        user.groups.add(group)

        return user
    
def validate_role(self, value):
    if not Group.objects.filter(name=value).exists():
        raise serializers.ValidationError("Invalid role")
    return value

# -------------------- Login Serializer --------------------
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            username=data.get('username'),
            password=data.get('password')
        )

        if not user:
            raise serializers.ValidationError("Invalid username or password")

        data['user'] = user
        return data


# -------------------- Client Serializer --------------------
class ClientSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = Client
        fields = "__all__"
        read_only_fields = ['ip_address', 'geo_location']

    
    def validate_mobile_no(self, value):
        value = str(value)
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("Mobile number must be 10 digits")
        return value

    def validate_gst_no(self, value):
        if len(value) != 15:
            raise serializers.ValidationError("GST number must be 15 characters")
        return value

    def validate_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Client name must be at least 3 characters")
        return value


# -------------------- Process Serializer --------------------
class ProcessSerializer(serializers.ModelSerializer):
    created_by = UserNestedSerializer(
        read_only=True
    )
    # created_by = serializers.ReadOnlyField(source='created_by.id')

    class Meta:
        model = Process
        fields = "__all__"
        
    def validate_process_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Process name cannot be empty")
        return value


        # fields = ['id', 'process_name', 'created_by', 'created_date']
     

# -------------------- Asset Serializer --------------------
class AssetSerializer(serializers.ModelSerializer):
    # created_by = serializers.ReadOnlyField(source='created_by.username')

    client_details = ClientNestedSerializer(source='client', read_only=True)
    process_details = ProcessNestedSerializer(source='process', read_only=True)
    created_by = UserNestedSerializer(read_only=True)

    class Meta:
        model = Asset
        fields = "__all__"



    def validate(self, data):
        if data.get('output_unit') and data.get('raw_material_unit'):
            if data['output_unit'] == data['raw_material_unit']:
                raise serializers.ValidationError(
                    "Output unit and Raw material unit cannot be same"
                )
        return data
    
    def validate(self, data):
        name = data.get('name')
        # client = data.get('client')

        if Asset.objects.filter(name=name).exists():
            raise serializers.ValidationError(
                "This asset name is already assigned to another client."
            )


        return data



# -------------------- ProductionLine Serializer --------------------
class ProductionLineSerializer(serializers.ModelSerializer):
    assets = AssetSerializer(many=True, read_only=True)
    client = ClientNestedSerializer(read_only=True)
    created_by = UserNestedSerializer(read_only=True)
    # created_by = serializers.ReadOnlyField(source='created_by.id')       #A read-only field that simply returns the field value.

    assets = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Asset.objects.all()
    )

    class Meta:
        model = ProductionLine
        fields = "__all__"

    def validate_assets(self, value):
        if len(value) == 0:
            raise serializers.ValidationError("At least one asset is required")
        return value
