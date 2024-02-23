from rest_framework import serializers

from expatsapp.models import User, Company, Review


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "rating",
            "comment",
        ]


class CompanySerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = [
            "name",
            "legal_name",
            "description",
            "category",
            "location",
            "rating_summary",
            "reviews",
        ]
