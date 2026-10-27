from rest_framework import serializers


class StrictCharField(serializers.CharField):
    def run_validation(self, data=serializers.empty):
        if data is not serializers.empty and not isinstance(data, str):
            self.fail('invalid')

        return super().run_validation(data)


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = StrictCharField()
    token = StrictCharField()
    password = StrictCharField(
        write_only=True,
        trim_whitespace=False,
    )
