from rest_framework import serializers

from apps.companies.models import Company

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


class ReviewCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "display_name"]


class MyReviewSerializer(serializers.ModelSerializer):
    company = ReviewCompanySerializer(read_only=True)
    approved = serializers.SerializerMethodField()

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
            "approved",
            "company",
        ]

    def get_approved(self, obj):
        return obj.approved_at is not None
