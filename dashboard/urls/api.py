"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.urls import path
from dashboard.api import GetDashboardData

urlpatterns = [
    path('get_dashboard_data', GetDashboardData.as_view(), name='api__get_dashboard_data'),
]
