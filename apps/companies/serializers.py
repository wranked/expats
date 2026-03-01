import cloudinary.utils
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Company, CompanyAdmin, Branch
from apps.locations.models import Address, Location

User = get_user_model()


# class ReviewSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Review
#         fields = [
#             "id",
#             "created_at",
#             "modified_at",
#             "rating",
#             "comment",
#             "start_date",
#             "end_date",
#             "is_public",
#         ]

#     def to_representation(self, instance):
#         data = super(ReviewSerializer, self).to_representation(instance)
#         if data.get("is_public"):
#             data["reviewer_display_name"] = instance.reviewer.display_name
#             data["reviewer_email"] = instance.reviewer.email
#             data["reviewer_avatar"] = instance.reviewer.picture
#         return data

# class AddressSerializer(serializers.ModelSerializer):
#     location = serializers.CharField(source="location.__str__", read_only=True)

#     class Meta:
#         model = Address
#         fields = [
#             "id",
#             "name",
#             "address_type",
#             "street",
#             "number",
#             "floor",
#             "apartment",
#             "building",
#             "postal_code",
#             "latitude",
#             "longitude",
#             "location",
#         ]


class BranchSerializer(serializers.ModelSerializer):
    address = serializers.CharField(source="address.__str__", read_only=True)
    location = serializers.CharField(source="location.__str__", read_only=True)

    class Meta:
        model = Branch
        fields = [
            "id",
            "name",
            "is_primary",
            "location",
            "address",
        ]

    

class CompanySerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    primary_location = serializers.SerializerMethodField()
    branches = BranchSerializer(many=True, required=False)
    
    class Meta:
        model = Company
        fields = [
            "id",
            "display_name",
            "id_name",
            "legal_name",
            "url",
            "description",
            "category",
            # "picture",
            "avatar",
            "avatar_url",
            "rating_summary",
            "primary_location",
            "branches",
            # "admins",
            "reviews_rating",
            "reviews_count",
            "blacklisted_at",
            "is_certified"
        ]
        read_only_fields = [
            "reviews_rating",
            "reviews_count",
            "blacklisted_at",
            "is_certified",
        ]

    def get_avatar_url(self, obj):
        if obj.avatar:
            return cloudinary.utils.cloudinary_url(obj.avatar.url)[0]
        return None

    def get_primary_location(self, obj):
        branch = obj.branches.filter(is_primary=True).first()
        return str(branch.location) if branch else None

    # def get_admins(self, obj):
    #     user = self.context["request"].user
    #     print("User:", user)
    #     if user.is_superuser or CompanyAdmin.objects.filter(user=user, company=obj).exists():
    #         return CompanyAdminSerializer(obj.admins.all(), many=True).data
    #     return []


class CompanyAdminSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source="user")

    class Meta:
        model = CompanyAdmin
        fields = [
            "id",
            # "company",
            "user_id",
            "user_email",
            "role",
            ]



class CompanyManageSerializer(serializers.ModelSerializer):
    
    avatar_url = serializers.SerializerMethodField()
    branches = BranchSerializer(many=True, required=False)
    
    admins = CompanyAdminSerializer(many=True)

    class Meta:
        model = Company
        fields = [
            "id",
            "display_name",
            "id_name",
            "legal_name",
            "url",
            "description",
            "category",
            # "picture",
            "avatar",
            "avatar_url",
            # "rating_summary",
            "branches",
            "admins",
        ]

    def get_avatar_url(self, obj):
        if obj.avatar:
            return cloudinary.CloudinaryImage(obj.avatar.public_id).build_url()
        return None
    
    def update(self, instance, validated_data):
        # if "admins" in validated_data:
        #     instance.admins.set(validated_data.pop("admins"))

        if "locations" in validated_data:
            instance.locations.set(validated_data.pop("locations"))

        return super().update(instance, validated_data)


# class MyReviewSerializer(serializers.ModelSerializer):
#     company = CompanySerializer(read_only=True)

#     class Meta:
#         model = Review
#         fields = [
#             "id",
#             "created_at",
#             "modified_at",
#             "rating",
#             "comment",
#             "start_date",
#             "end_date",
#             "is_public",
#             "company",
#         ]


