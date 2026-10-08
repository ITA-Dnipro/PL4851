from rest_framework import serializers

from content.sections.models import (
    LandingBanner,
    LandingForWhomCard,
    LandingForWhomSection,
    LandingHero,
    LandingHeroImage,
    LandingWhyWorthItem,
    LandingWhyWorthSection,
)


class LandingHeroImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandingHeroImage
        fields = ('title', 'url')


class LandingHeroSerializer(serializers.ModelSerializer):
    hero_images = LandingHeroImageSerializer(source='images', many=True)

    class Meta:
        model = LandingHero
        fields = ('title', 'subtitle', 'cta_text', 'cta_url', 'hero_images')


class LandingBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandingBanner
        fields = ('title', 'cta_text', 'cta_url')


class LandingForWhomCardSerializer(serializers.ModelSerializer):
    desc = serializers.CharField(source='description')

    class Meta:
        model = LandingForWhomCard
        fields = ('icon', 'title', 'desc')


class LandingForWhomSectionSerializer(serializers.ModelSerializer):
    items = LandingForWhomCardSerializer(source='cards', many=True)

    class Meta:
        model = LandingForWhomSection
        fields = ('title', 'items')


class LandingWhyWorthItemSerializer(serializers.ModelSerializer):
    desc = serializers.CharField(source='description')

    class Meta:
        model = LandingWhyWorthItem
        fields = ('title', 'desc')


class LandingWhyWorthSectionSerializer(serializers.ModelSerializer):
    items = LandingWhyWorthItemSerializer(many=True)

    class Meta:
        model = LandingWhyWorthSection
        fields = ('title', 'items')
