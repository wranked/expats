from rest_framework import serializers

from expatsapp.models import Company, Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"


class CompanySerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "legal_name",
            "description",
            "category",
            "location",
            "rating_summary",
            "reviews",
        ]
