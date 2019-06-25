# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CashPickup',
            fields=[
                ('requestID', models.AutoField(serialize=False, primary_key=True)),
                ('lat', models.DecimalField(default=0, verbose_name='Latitude', max_digits=10, decimal_places=8)),
                ('lng', models.DecimalField(default=0, verbose_name='Longitude', max_digits=11, decimal_places=8)),
                ('street', models.CharField(max_length=30)),
                ('area', models.CharField(max_length=70)),
                ('country', models.CharField(max_length=5)),
                ('amount', models.DecimalField(default=0, max_digits=7, decimal_places=2)),
                ('status', models.CharField(max_length=50)),
                ('phone', models.CharField(max_length=20)),
                ('dateCreated', models.DateTimeField(default=django.utils.timezone.now)),
                ('code', models.CharField(max_length=6)),
                ('currency', models.CharField(max_length=6)),
            ],
            options={
                'verbose_name': 'Cash Pickup',
                'verbose_name_plural': 'Cash Pickup',
            },
        ),
        migrations.CreateModel(
            name='CurrencyData',
            fields=[
                ('currencyID', models.AutoField(serialize=False, primary_key=True)),
                ('currency_code', models.CharField(max_length=4)),
                ('currency_rate', models.DecimalField(default=0, max_digits=12, decimal_places=6)),
                ('dateUpdated', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'Currency Mid-Market Rates',
                'verbose_name_plural': 'Currency Mid-Market Rates',
            },
        ),
        migrations.CreateModel(
            name='PayoutPartnerDetails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lat', models.DecimalField(default=0, verbose_name='Latitude', max_digits=10, decimal_places=8)),
                ('lng', models.DecimalField(default=0, verbose_name='Longitude', max_digits=11, decimal_places=8)),
                ('bank_account', models.CharField(max_length=30)),
                ('street', models.CharField(max_length=30)),
                ('area', models.CharField(max_length=30)),
                ('country', models.CharField(max_length=5)),
            ],
            options={
                'verbose_name': 'PayoutPartner Details',
                'verbose_name_plural': 'PayoutPartner Details',
            },
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('requestID', models.AutoField(serialize=False, primary_key=True)),
                ('lat', models.DecimalField(default=0, verbose_name='Latitude', max_digits=10, decimal_places=8)),
                ('lng', models.DecimalField(default=0, verbose_name='Longitude', max_digits=11, decimal_places=8)),
                ('street', models.CharField(max_length=30)),
                ('area', models.CharField(max_length=70)),
                ('country', models.CharField(max_length=5)),
                ('amount', models.DecimalField(default=0, max_digits=7, decimal_places=2)),
                ('status', models.CharField(max_length=50)),
                ('isAssigned', models.BooleanField(default=False)),
                ('dateCreated', models.DateTimeField(default=django.utils.timezone.now)),
                ('phone', models.CharField(max_length=20)),
                ('code', models.CharField(max_length=6)),
                ('currency', models.CharField(max_length=6)),
            ],
            options={
                'verbose_name': 'Request',
                'verbose_name_plural': 'Requests',
            },
        ),
        migrations.CreateModel(
            name='RequestAssigned',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dateCreated', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'Request Assigned',
                'verbose_name_plural': 'Requests Assigned',
            },
        ),
        migrations.CreateModel(
            name='Transfers',
            fields=[
                ('transferID', models.AutoField(serialize=False, primary_key=True)),
                ('amount', models.DecimalField(default=0, max_digits=7, decimal_places=2)),
                ('due', models.DateTimeField()),
            ],
            options={
                'verbose_name': 'Transfers',
                'verbose_name_plural': 'Transfers',
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phoneNumber', models.CharField(max_length=18)),
                ('isVerified', models.BooleanField(default=False)),
                ('isPayoutPartner', models.BooleanField(default=False)),
                ('dateCreated', models.DateTimeField(default=django.utils.timezone.now)),
                ('pendingPayment', models.BooleanField(default=False)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
            },
        ),
        migrations.CreateModel(
            name='UserVerification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pinNumberSent', models.CharField(max_length=7)),
                ('trialAttempts', models.IntegerField(default=0)),
                ('emailCodeSent', models.CharField(default='', max_length=7)),
                ('isBlocked', models.BooleanField(default=False)),
                ('userprofile', models.ForeignKey(to='Xeemit.UserProfile')),
            ],
            options={
                'verbose_name': 'User Verification',
                'verbose_name_plural': 'User Verification',
            },
        ),
        migrations.AddField(
            model_name='transfers',
            name='assignedTo',
            field=models.ForeignKey(related_name='PayoutPartner', to='Xeemit.UserProfile'),
        ),
        migrations.AddField(
            model_name='requestassigned',
            name='PayoutPartner',
            field=models.ForeignKey(to='Xeemit.UserProfile'),
        ),
        migrations.AddField(
            model_name='requestassigned',
            name='requestID',
            field=models.OneToOneField(to='Xeemit.Request'),
        ),
        migrations.AddField(
            model_name='request',
            name='requestUser',
            field=models.ForeignKey(to='Xeemit.UserProfile'),
        ),
        migrations.AddField(
            model_name='payoutpartnerdetails',
            name='userprofile',
            field=models.ForeignKey(to='Xeemit.UserProfile'),
        ),
        migrations.AddField(
            model_name='cashpickup',
            name='assignedTo',
            field=models.ForeignKey(related_name='Payout_Partner', to='Xeemit.UserProfile'),
        ),
        migrations.AddField(
            model_name='cashpickup',
            name='requestUser',
            field=models.ForeignKey(related_name='Requester', to='Xeemit.UserProfile'),
        ),
    ]
