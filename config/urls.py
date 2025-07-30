# from django.urls import path
# from . import views

# urlpatterns = [
#     path('bot-config/', views.bot_config_view, name='bot_config'),
# ]



# from django.urls import path
# from .views import bot_config_view

# print("Form submitted")  # Debug log


# urlpatterns = [
#     path('', bot_config_view, name='bot_config'),
# ]

# from django.urls import path
# from .views import bot_config_view

# urlpatterns = [
#     path('', bot_config_view, name='bot_config'),
# ]
# from django.urls import path
# from .views import bot_config_view

# urlpatterns = [
#     path('', bot_config_view, name='bot_config'),  # Default to ID=1
#     path('<int:pk>/', bot_config_view, name='edit_bot_config'),  # Edit specific config
   
#     path('', bot_config_view, kwargs={'pk': 1}, name='bot_config'),  # Home → config 1
#     path('edit_bot_config/', bot_config_view, kwargs={'pk': 1}, name='edit_bot_config'),
#     path('<int:pk>/', bot_config_view, name='edit_specific_config'),


# ]
from django.urls import path
from .views import bot_config_view

urlpatterns = [
    path('', bot_config_view, name='bot_config'),
]

