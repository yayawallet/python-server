from django.urls import path
from ..views import lookup_views

urlpatterns = [
    path('lookup/gender', lookup_views.proxy_gender_lookup, name='gender-lookup'),
    path('lookup/region', lookup_views.proxy_region_lookup, name='region-lookup'),
    path('lookup/business-categories', lookup_views.proxy_business_categories_lookup, name='business-categories-lookup'),
]