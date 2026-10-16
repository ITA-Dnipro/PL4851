import bleach
import markdown
from django.conf import settings
from rest_framework import serializers

from startups.models import StartupProfile

INDUSTRIES_FIELD_CONFIG = serializers.SlugRelatedField(
    many=True, read_only=True, slug_field='industry_name'
)

ALLOWED_HTML_TAGS = [
    'p',
    'b',
    'i',
    'strong',
    'em',
    'u',
    'br',
    'h1',
    'h2',
    'h3',
    'h4',
    'ul',
    'ol',
    'li',
    'a',
]
ALLOWED_HTML_ATTRIBUTES = {'a': ['href', 'title', 'target', 'rel']}


def get_startup_logo_url(obj):
    if obj.logo:
        return obj.logo.url

    return f'{settings.MEDIA_URL}thumbs/placeholder.jpg'


class StartupProfileSerializer(serializers.ModelSerializer):
    """A lightweight serializer for a list of startups."""

    industries = INDUSTRIES_FIELD_CONFIG
    logo = serializers.SerializerMethodField()
    location = serializers.CharField(source='get_location_display', read_only=True)

    def get_logo(self, obj):
        """Returns the URL of the startup's logo or a default placeholder."""

        return get_startup_logo_url(obj)

    class Meta:
        model = StartupProfile
        fields = [
            'startup_id',
            'startup_name',
            'short_description',
            'logo',
            'location',
            'industries',
        ]


class StartupPublicProfileSerializer(serializers.ModelSerializer):
    """Full serializer for a startup's public profile"""

    industries = INDUSTRIES_FIELD_CONFIG
    logo = serializers.SerializerMethodField()
    hero_image = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    projects_count = serializers.SerializerMethodField()
    contact = serializers.SerializerMethodField()
    about_html = serializers.SerializerMethodField()

    class Meta:
        model = StartupProfile
        fields = [
            'startup_id',
            'startup_name',
            'slug',
            'hero_image',
            'logo',
            'short_description',
            'about_html',
            'contact',
            'website',
            'industries',
            'followers_count',
            'projects_count',
            'created_at',
        ]

    def get_about_html(self, obj):
        """Returns clean startup description"""
        if not obj.startup_description:
            return ''

        html_content = markdown.markdown(obj.startup_description)
        clean_html = bleach.clean(
            html_content,
            tags=ALLOWED_HTML_TAGS,
            attributes=ALLOWED_HTML_ATTRIBUTES,
            strip=True,
        )

        return clean_html

    def get_logo(self, obj):
        """Returns the URL of the startup's logo or a default placeholder."""

        return get_startup_logo_url(obj)

    def get_hero_image(self, obj):
        """Returns the URL of the startup's hero_image or a default placeholder"""
        if obj.hero_image:
            return obj.hero_image.url

        return f'{settings.MEDIA_URL}thumbs/hero.placeholder.jpg'

    def get_contact(self, obj):
        """Creates a nested dictionary of contacts."""
        formatted_phone = f'+{obj.startup_phone}' if obj.startup_phone else ''

        return {'email': obj.startup_email, 'phone': formatted_phone}

    def get_followers_count(self, obj):
        """Counts the number of subscribers"""

        return getattr(obj, '_followers_count', 0)

    def get_projects_count(self, obj):
        """Counts the number of projects."""

        if hasattr(obj, '_projects_count'):
            return obj._projects_count

        return obj.projects.exclude(status='draft').count()
