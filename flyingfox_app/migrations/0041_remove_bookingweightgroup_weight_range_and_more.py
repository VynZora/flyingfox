from django.db import migrations, models


# =========================================================
# COPY OLD WEIGHT RANGE DATA TO NEW STATIC RANGE KEY
# =========================================================

def populate_range_key(apps, schema_editor):

    BookingWeightGroup = apps.get_model(
        "flyingfox_app",
        "BookingWeightGroup"
    )

    for group in BookingWeightGroup.objects.all():

        group.range_key = (
            f"{group.min_weight}-"
            f"{group.max_weight}"
        )

        group.save(
            update_fields=["range_key"]
        )


class Migration(migrations.Migration):

    dependencies = [
        (
            "flyingfox_app",
            "0040_chatsession_context",
        ),
    ]

    operations = [

        # =====================================================
        # 1. ADD NEW FIELD TEMPORARILY AS NULLABLE
        # =====================================================

        migrations.AddField(
            model_name="bookingweightgroup",
            name="range_key",
            field=models.CharField(
                max_length=20,
                null=True,
                blank=True,
            ),
        ),


        # =====================================================
        # 2. COPY EXISTING DATA
        #
        # Example:
        # 30 + 50 -> "30-50"
        # =====================================================

        migrations.RunPython(
            populate_range_key,
            migrations.RunPython.noop,
        ),


        # =====================================================
        # 3. REMOVE OLD CONSTRAINT FIRST
        #
        # IMPORTANT:
        # This MUST happen before removing weight_range.
        # =====================================================

        migrations.RemoveConstraint(
            model_name="bookingweightgroup",
            name="unique_booking_participant_weight_range",
        ),


        # =====================================================
        # 4. REMOVE OLD FOREIGN KEY
        # =====================================================

        migrations.RemoveField(
            model_name="bookingweightgroup",
            name="weight_range",
        ),


        # =====================================================
        # 5. DELETE OLD PARTICIPANT WEIGHT RANGE MODEL
        # =====================================================

        migrations.DeleteModel(
            name="ParticipantWeightRange",
        ),


        # =====================================================
        # 6. CHANGE PARTICIPANT COUNT DEFAULT
        # =====================================================

        migrations.AlterField(
            model_name="bookingweightgroup",
            name="participant_count",
            field=models.PositiveIntegerField(
                default=1,
            ),
        ),


        # =====================================================
        # 7. MAKE RANGE KEY REQUIRED
        # =====================================================

        migrations.AlterField(
            model_name="bookingweightgroup",
            name="range_key",
            field=models.CharField(
                max_length=20,
                choices=[
                    (
                        "30-50",
                        "30–50 KG",
                    ),
                    (
                        "50-70",
                        "50–70 KG",
                    ),
                    (
                        "70-90",
                        "70–90 KG",
                    ),
                    (
                        "90-110",
                        "90–110 KG",
                    ),
                ],
            ),
        ),


        # =====================================================
        # 8. ADD NEW UNIQUE CONSTRAINT
        # =====================================================

        migrations.AddConstraint(
            model_name="bookingweightgroup",
            constraint=models.UniqueConstraint(
                fields=(
                    "booking",
                    "range_key",
                ),
                name="unique_booking_weight_range",
            ),
        ),

    ]