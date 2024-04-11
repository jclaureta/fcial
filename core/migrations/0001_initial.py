# Generated by Django 3.1.3 on 2020-11-29 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LastFace',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_face', models.CharField(max_length=200)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=70)),
                ('last_name', models.CharField(max_length=70)),
                ('age', models.DateField()),
                ('phone', models.BigIntegerField()),
                ('email', models.EmailField(max_length=254)),
                ('term', models.IntegerField()),
                ('program', models.CharField(max_length=200)),
                ('status', models.CharField(choices=[('employee', 'employee'), ('professor', 'professor')], default='employee', max_length=20, null=True)),
                ('present', models.BooleanField(default=False)),
                ('image', models.ImageField(upload_to='')),
                ('updated', models.DateTimeField(auto_now=True)),
                ('section', models.CharField(max_length=200)),
                ('studentid', models.CharField(max_length=200))
            ],
        ),
    ]
