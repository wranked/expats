from rest_framework import serializers

from apps.companies.serializers import CompanySerializer

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    is_public = serializers.BooleanField(write_only=True, default=False)

    class Meta:
        model = Review
        fields = [
            "id",
            "created_at",
            "modified_at",
            "rating",
            "comment",
            "start_date",
            "end_date",
            "is_public",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.is_public:
            data["reviewer_display_name"] = instance.reviewer.display_name
            data["reviewer_email"] = instance.reviewer.email
            data["reviewer_avatar"] = instance.reviewer.picture
        return data


class MyReviewSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "created_at",
            "modified_at",
            "rating",
            "comment",
            "start_date",
            "end_date",
            "is_public",
            "company",
        ]
