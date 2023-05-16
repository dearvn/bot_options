"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('setting-post', views.post_setting),
    path('options-stream-sub', views.post_suboptions),
    path('options-stream-ubsub', views.post_unsuboptions),
    path('option-chain-get', views.get_option_chain),
    path('expirations-get', views.get_expirations),
    path('quote-get', views.get_quote),
    path('quote-stream-get', views.get_quote_stream),
    path('options-stream-get', views.get_options_stream),
    path('open-get', views.get_open),

    path('order-options', views.create_order_options),
    path('get-order-options', views.get_order_options),
    path('cancel-order-options', views.cancel_order_options),

]
