# Generated by Django 5.1.6 on 2025-02-21 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="JobApplication",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(max_length=80)),
                ("last_name", models.CharField(max_length=80)),
                ("email", models.EmailField(max_length=254)),
                ("date", models.DateField()),
                ("occupation", models.CharField(max_length=80)),
            ],
            options={
                "db_table": "job_applications",
            },
        ),
    ]
