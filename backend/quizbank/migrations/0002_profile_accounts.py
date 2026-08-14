import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def delete_legacy_profiles(apps, schema_editor):
    """Pre-account profiles have no way to map onto a real login (no
    credentials were ever attached to them), so they can't survive the move
    to one-profile-per-account. Attempt/QuestionSeen cascade on delete.
    """
    Profile = apps.get_model("quizbank", "Profile")
    Profile.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("quizbank", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(delete_legacy_profiles, migrations.RunPython.noop),
        migrations.AddField(
            model_name="profile",
            name="preferred_topic",
            field=models.CharField(blank=True, default="", max_length=64),
        ),
        migrations.AddField(
            model_name="profile",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="profile",
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
    ]
