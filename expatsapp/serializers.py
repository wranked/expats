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
            "is_anonymous",  # TODO: Replace for 'is_public'
        ]

    def to_representation(self, instance):
        data = super(ReviewSerializer, self).to_representation(instance)
        if not data.get("is_anonymous"):
            data["reviewer_display_name"] = instance.reviewer.display_name
            data["reviewer_email"] = instance.reviewer.email
            data["reviewer_avatar"] = instance.reviewer.picture
        return data


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
            "picture",
            "rating_summary",
        ]


class JobSerializer(serializers.ModelSerializer):

    company_name = serializers.ReadOnlyField(source="company.display_name")
    company_picture = serializers.ReadOnlyField(source="company.picture")

    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "company_name",
            "company_picture",
            "created_at",
        ]


class JobDetailsSerializer(serializers.ModelSerializer):

    company_name = serializers.ReadOnlyField(source="company.display_name")
    company_picture = serializers.ReadOnlyField(source="company.picture")

    class Meta:
        model = Job
        fields = [
            "title",
            "company_name",
            "company_picture",
            "description",
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
