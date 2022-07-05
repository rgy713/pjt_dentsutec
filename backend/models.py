from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.


class Country(models.Model):
    country_id = models.CharField(max_length=255)
    country_name = models.CharField(max_length=255)
    status = models.SmallIntegerField(default=1)
    note = models.CharField(max_length=255)

    class Meta:
        db_table = 't_country'


class Category(models.Model):
    category_id = models.CharField(max_length=255)
    category_name = models.CharField(max_length=255)
    status = models.SmallIntegerField(default=1)
    note = models.CharField(max_length=255)

    class Meta:
        db_table = 't_category'


class Segment(models.Model):
    segment_name = models.CharField(max_length=255)
    status = models.SmallIntegerField(default=1)
    note = models.CharField(max_length=255)

    class Meta:
        db_table = 't_segment'


class Company(models.Model):
    company_name = models.CharField(max_length=255)
    status = models.SmallIntegerField(default=1)
    note = models.CharField(max_length=255)

    class Meta:
        db_table = 't_company'


class Client(models.Model):
    client_name = models.CharField(max_length=255, null=True)
    company = models.ForeignKey(Company, db_column='company', on_delete=models.CASCADE, unique=False, null=True)
    register = models.ForeignKey(User, db_column='register', on_delete=models.CASCADE, unique=False, null=True)
    status = models.SmallIntegerField(default=1)
    note = models.CharField(max_length=255)

    class Meta:
        db_table = 't_client'


class Profile(models.Model):
    user = models.OneToOneField(User, db_column='user', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, db_column='country', on_delete=models.CASCADE, unique=False, null=True)
    note = models.CharField(max_length=255)

    class Meta:
        db_table = 't_user_profile'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class User_setting(models.Model):
    user = models.OneToOneField(User, db_column='user', on_delete=models.CASCADE)
    segments = models.TextField()
    companies = models.TextField()
    countries = models.TextField()

    class Meta:
        db_table = 't_user_setting'


class Project(models.Model):
    project_id = models.CharField(max_length=255)
    project_name = models.CharField(max_length=255, null=True)
    register = models.ForeignKey(User, db_column='register', on_delete=models.CASCADE, unique=False, null=True)
    client = models.ForeignKey(Client, db_column='client', on_delete=models.SET_NULL, unique=False, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    outline = models.TextField()
    result = models.CharField(max_length=255)
    category = models.ForeignKey(Category, db_column='category', on_delete=models.CASCADE, unique=False, null=True)
    segment = models.ForeignKey(Segment, db_column='segment', on_delete=models.CASCADE, unique=False, null=True)
    status = models.SmallIntegerField(default=1)
    note = models.CharField(max_length=255)

    class Meta:
        db_table = 't_project'


class Media(models.Model):
    media_id = models.CharField(max_length=255)
    type = models.SmallIntegerField(default=0)
    url = models.CharField(max_length=255)
    thumb = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    hash_tag = models.CharField(max_length=255)
    project = models.ForeignKey(Project, db_column='project', on_delete=models.CASCADE, unique=False, null=True)
    register = models.ForeignKey(User, db_column='register', on_delete=models.CASCADE, unique=False, null=True)
    regist_date = models.DateTimeField()
    status = models.SmallIntegerField(default=1)
    note = models.CharField(max_length=255)

    class Meta:
        db_table = 't_media'

