from rest_framework import serializers

from expatsapp.models import Company, Review, Job


class ReviewSerializer(serializers.ModelSerializer):
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
            "is_anonymous",
        ]


class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = [
            "id",
            "display_name",
            "id_name",
            "legal_name",
            "description",
            "category",
            # "location",
            "rating_summary",
        ]


class JobSerializer(serializers.ModelSerializer):

    company_name = serializers.ReadOnlyField(source="company.display_name")

    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "company_name",
            "created_at",
        ]


class JobDetailsSerializer(serializers.ModelSerializer):

    company_name = serializers.ReadOnlyField(source="company.display_name")

    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "company_name",
            "created_at",
            "description",
            "expires_on",
            "hiring_type",
            "hours",
            "duration",
            "place",
            "has_sponsorship",
            "has_accommodation",
            "has_meal",
        ]
