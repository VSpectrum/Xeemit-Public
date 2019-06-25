"""ProjXeemit URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from Xeemit.views import *

""" Admin Site Text Modifications """

admin.site.index_title = 'Xeemit Administration'
admin.site.site_header = 'Xeemit Administration'
admin.site.site_title = 'Xeemit Admin'


urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^password_required/$', 'password_required.views.login'),

    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^user-registration/$', registration),
    url(r'^user-login/$', login),
    url(r'^logout/$', logout),
    url(r'^$', homepage),

    url(r'^chat$', chatsystem),
    url(r'^phone-validation/$', phonevalidation),
    url(r'^email-validation/$', emailvalidation),
    url(r'^partner-registration/$', partnerregistrationvalidation),

    url(r'^user/(?P<username>([A-Za-z0-9_\.-]+))/$', userhome),
    url(r'^request$', requesthandler),
    url(r'^cashpayment-conversion/$', cashpaymentconversion),
    url(r'^delivery/$', delivery),

]
