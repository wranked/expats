import cloudinary
from rest_framework import serializers
from django.contrib.auth import get_user_model
from jobs.models import Job


class JobSerializer(serializers.ModelSerializer):

    company_name = serializers.ReadOnlyField(source="company.display_name")
    company_avatar_url = serializers.SerializerMethodField()
    location = serializers.StringRelatedField()


    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "company",   # TODO: Check if it is necessary to include this field
            "company_name",
            "company_avatar_url",
            "location",
            "created_at",
        ]

    def get_company_avatar_url(self, obj):
        if obj.company.avatar:
            return cloudinary.utils.cloudinary_url(obj.company.avatar.url)[0]
        return None


class JobDetailsSerializer(serializers.ModelSerializer):

    company_name = serializers.ReadOnlyField(source="company.display_name")
    company_avatar_url = serializers.SerializerMethodField()
    location = serializers.StringRelatedField()

    class Meta:
        model = Job
        fields = [
            "title",
            "company",
            "company_name",
            "company_avatar_url",
            "description",
            "created_at",
            "expires_on",
            "hiring_type",
            "hours",
            "duration",
            "place",
            "has_sponsorship",
            "has_accommodation",
            "has_meal",
            "location",
        ]

        read_only_fields = [
            "id",
            "company_name",
            "company_picture",
            "created_at",
        ]

    def get_company_avatar_url(self, obj):
        if obj.company.avatar:
            return cloudinary.utils.cloudinary_url(obj.company.avatar.url)[0]
        return None
