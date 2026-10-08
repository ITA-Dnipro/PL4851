from rest_framework import serializers

from startups.models import StartupProfile


class StartupProfileSerializer(serializers.ModelSerializer):
    industries = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='slug'
    )

    logo = serializers.SerializerMethodField()
    location = serializers.CharField(source='get_location_display', read_only=True)

    def get_logo(self, obj):
        """Returns the URL of the startup's logo or a default placeholder."""

        return obj.logo.url if obj.logo else '/media/thumbs/placeholder.jpg'

    class Meta:
        model = StartupProfile
        fields = [
            'startup_id',
            'startup_name',
            'startup_description',
            'logo',
            'location',
            'industries',
        ]
