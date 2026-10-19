from rest_framework import serializers

from investors.models import InvestorProfile


class InvestorProfileListSerializer(serializers.ModelSerializer):
    """A lightweight serializer for a list of investors."""

    class Meta:
        model = InvestorProfile
        fields = [
            'investor_id',
            'investor_name',
            'investor_type',
            'investment_min',
        ]


class InvestorProfileDetailSerializer(serializers.ModelSerializer):
    """Full serializer for a single investor profile."""

    contact = serializers.SerializerMethodField()

    class Meta:
        model = InvestorProfile
        fields = [
            'investor_id',
            'investor_name',
            'investor_type',
            'investor_description',
            'contact',
            'investment_min',
            'is_verified',
        ]

    def get_contact(self, obj):
        """Returns the public contacts with the phone in international format."""
        phone = f'+{obj.investor_phone}' if obj.investor_phone else ''

        return {'phone': phone}
