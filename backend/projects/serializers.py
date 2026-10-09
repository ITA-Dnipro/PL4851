from django.conf import settings
from rest_framework import serializers

from projects.models import Project


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for the Project model, including a method to retrieve the logo URL."""

    logo = serializers.SerializerMethodField()

    def get_logo(self, obj):
        """Returns the URL of the startup's logo or a default placeholder."""

        if obj.logo:
            return obj.logo.url

        return f'{settings.MEDIA_URL}thumbs/placeholder.jpg'

    class Meta:
        model = Project
        fields = [
            'project_id',
            'project_title',
            'status',
            'logo',
            'short_description',
        ]
