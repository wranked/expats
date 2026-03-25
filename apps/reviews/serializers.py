from rest_framework import serializers

from apps.companies.models import Company

from .models import Review


class ReviewerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review.reviewer.field.related_model
        fields = ["display_name", "email", "picture"]


class ReviewSerializer(serializers.ModelSerializer):
    is_public = serializers.BooleanField(write_only=True, default=False)
    is_approved = serializers.SerializerMethodField()
    reviewer = serializers.SerializerMethodField()

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
            "is_approved",
            "reviewer",
        ]

    def get_is_approved(self, obj):
        return obj.approved_at is not None

    def get_reviewer(self, obj):
        if obj.is_public:
            return ReviewerSerializer(obj.reviewer).data
        return None


class ReviewCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "display_name"]


class MyReviewSerializer(serializers.ModelSerializer):
    company = ReviewCompanySerializer(read_only=True)
    is_approved = serializers.SerializerMethodField()

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
            "is_approved",
            "company",
        ]

    def get_is_approved(self, obj):
        return obj.approved_at is not None
