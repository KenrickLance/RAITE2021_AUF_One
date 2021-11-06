from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from django.contrib.auth.models import User

import datetime



class ModelAllowDisplayInfo(models.Model):
    def display_info(self):
        info = {}
        for item in self._meta.fields:
            info[item.verbose_name] = self.__getattribute__(item.name)
        return info

    class Meta:
        abstract=True

class GenericModelMain(ModelAllowDisplayInfo):
    sex_choices = [
        ('',''),
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    first_name = models.CharField('First name',max_length=254,)
    middle_name = models.CharField('Middle name', max_length=254)
    last_name = models.CharField('Last name', max_length=254)
    email = models.EmailField('Email address', max_length=254)
    sex = models.CharField('Sex', max_length=254, choices=sex_choices)
    birth_date = models.DateField('Date of birth')
    employment_date = models.DateField('Employment date', auto_now_add=True)
    termination_date = models.DateField('Termination date', default=timezone.now()+datetime.timedelta(days=365*3))

    def full_name(self):
        return self.first_name + ' ' + self.middle_name + ' ' + self.last_name


    def __str__(self):
        return f'{self.last_name}, {self.first_name} {self.middle_name}'

class PeopleModel(ModelAllowDisplayInfo):
    sex_choices = [
        ('',''),
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    user_info = models.ForeignKey(User,related_name='user_info', on_delete=models.SET_NULL, null=True)
    birth_date = models.DateField('Date of birth')
    sex = models.CharField('Sex', max_length=254, choices=sex_choices)

    phone = models.CharField('Phone number', max_length=254)

    address_full = models.CharField('Full address', max_length=1000)
    address_barangay = models.CharField('Barangay', max_length=1000)
    address_city = models.CharField('City/Municipality', max_length=1000)
    address_province = models.CharField('Province', max_length=1000)
    address_zip = models.CharField('Zip code', max_length=4)
    government_id = models.FileField('Photo of government-issued ID',upload_to='people_id/')

    def full_name(self):
        return self.first_name + ' ' + self.middle_name + ' ' + self.last_name


    def __str__(self):
        return f'{self.last_name}, {self.first_name} {self.middle_name}'        

class VaccineModel(ModelAllowDisplayInfo):
    brand_choices = [
        ('',''),
        ('Moderna','Moderna'),
        ('Novarax','Novarax'),
        ('Oxford AstraZeneca','Oxford AstraZeneca'),
        ('Pfizer-BioNTech','Pfizer-BioNTech'),
        ('Sinopharm','Sinopharm'),
        ('Sinovac','Sinovac'),
        ('Sputnik V','Sputnik V'),
    ]
    personal_info = models.ForeignKey(GenericModelMain, default='', related_name='personal_info', on_delete=models.SET_NULL, null=True, verbose_name='Personal Identifier')
    brand = models.CharField('Brand', max_length=254, choices=brand_choices)
    first_dose_date = models.DateField('Date of 1st dose')
    second_dose_date = models.DateField('Date of 2nd dose',null=True, blank=True)
    status = models.CharField('Status', blank=True, default='', max_length=100)
    vaccine_card_id = models.FileField('Photo of vaccine card',upload_to='vaccine_id/')

   

    def __str__(self):
        return f'{self.personal_info.last_name}, {self.personal_info.first_name} {self.personal_info.middle_name}'        

class EstablishmentModel(ModelAllowDisplayInfo):
    user_info = models.ForeignKey(User,related_name='user_info_establishment', on_delete=models.SET_NULL, null=True)
    name = models.CharField('Name of establishment', max_length=1000)
    address_full = models.CharField('Full address', max_length=1000)
    address_barangay = models.CharField('Barangay', max_length=1000)
    address_city = models.CharField('City/Municipality', max_length=1000)
    address_province = models.CharField('Province', max_length=1000)
    address_zip = models.CharField('Zip code', max_length=4)

    def __str__(self):
        return f'{self.name}'

class HealthcareModel(ModelAllowDisplayInfo):
    user_info = models.ForeignKey(User,related_name='user_info_healthcare', on_delete=models.SET_NULL, null=True)
    name = models.CharField('Name of healthcare organization', max_length=1000)
    address_full = models.CharField('Full address', max_length=1000)
    address_barangay = models.CharField('Barangay', max_length=1000)
    address_city = models.CharField('City/Municipality', max_length=1000)
    address_province = models.CharField('Province', max_length=1000)
    address_zip = models.CharField('Zip code', max_length=4)

    def __str__(self):
        return f'{self.name}'
    
class RoleModel(ModelAllowDisplayInfo):
    user_info = models.ForeignKey(User,related_name='user_info_role', on_delete=models.SET_NULL, null=True)
    role = models.CharField(null=True, default='', max_length=40, blank=True)

class TracingModel(ModelAllowDisplayInfo):
    establishment = models.CharField(null=True, default='', max_length=400, blank=True)
    user_info = models.CharField(null=True, default='', max_length=400, blank=True)
    date = models.DateTimeField('Entry date', auto_now_add=True)


class GenericModelForeign(ModelAllowDisplayInfo):
    second_engineer = models.ForeignKey(GenericModelMain, default='', related_name='second_engineer', on_delete=models.SET_NULL, null=True, verbose_name='Second engineer')
    engine_cadet = models.ManyToManyField(GenericModelMain, default='', related_name='engine_cadet', verbose_name='Engine cadet')

