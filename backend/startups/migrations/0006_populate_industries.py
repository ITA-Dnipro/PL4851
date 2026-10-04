from django.db import migrations


def populate_default_industries(apps, _):
    Industry = apps.get_model('startups', 'Industry')
    from startups.models import Industry as IndustryModel
    IndustryType = IndustryModel.IndustryType
    for code, label in IndustryType.choices:
        Industry.objects.get_or_create(
            slug=code,
            defaults={'industry_name': label}
        )


def rollback_default_industries(apps, _):
    Industry = apps.get_model('startups', 'Industry')
    Industry.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('startups', '0005_industry_remove_startupprofile_startup_industry_idx_and_more'),
    ]
    operations = [
        migrations.RunPython(populate_default_industries, rollback_default_industries),
    ]
