from rest_framework import serializers

from dashboard.models import SavedProject


class SavedProjectSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='project.project_id', read_only=True)
    saved_id = serializers.IntegerField(source='saved_project_id', read_only=True)
    type = serializers.SerializerMethodField()
    title = serializers.CharField(source='project.project_title', read_only=True)
    slug = serializers.CharField(source='project.startup.slug', read_only=True)
    thumbnail_url = serializers.SerializerMethodField()
    short_description = serializers.CharField(
        source='project.short_description', read_only=True
    )
    location = serializers.CharField(source='project.startup.location', read_only=True)
    tags = serializers.SerializerMethodField()

    class Meta:
        model = SavedProject
        fields = [
            'id',
            'saved_id',
            'type',
            'title',
            'slug',
            'thumbnail_url',
            'short_description',
            'location',
            'tags',
            'saved_at',
        ]

    def get_type(self, obj):
        return 'project'

    def get_thumbnail_url(self, obj):
        logo = obj.project.logo
        if not logo:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(logo.url) if request else logo.url

    def get_tags(self, obj):
        return [i.slug for i in obj.project.startup.industries.all()]


class SaveItemSerializer(serializers.Serializer):
    target_type = serializers.ChoiceField(choices=['project'], default='project')
    target_id = serializers.IntegerField()
