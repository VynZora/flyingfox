from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("flyingfox_app", "0009_alter_galleryitem_options_and_more"),
    ]

    operations = [

        migrations.AlterModelOptions(
            name="galleryitem",
            options={
                "ordering": ["-uploaded_at"],
            },
        ),

        migrations.AddField(
            model_name="galleryitem",
            name="uploaded_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),

    ]