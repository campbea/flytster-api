from django.conf.urls import include, url
from django.contrib import admin

from trips.views import TripSearchListCreate, TripSearchRetrieveDestroy
from users.views import RegisterUser, LoginUser, LogoutUser, GetUpdateUser


urlpatterns = [
    url(r'^api/v1/', include([
        url(r'^user/register/?$', RegisterUser.as_view(), name='register'),
        url(r'^user/login/?$', LoginUser.as_view(), name='login'),
        url(r'^user/logout/?$', LogoutUser.as_view(), name='logout'),
        url(r'^user/?$', GetUpdateUser.as_view(), name='get_update_user'),

        url(r'^trip/search/?$', TripSearchListCreate.as_view(), name='trip_search_list_create'),
        url(r'^trip/search/(?P<pk>[0-9]+)/?$', TripSearchRetrieveDestroy.as_view(), name='trip_search_retrieve_destroy'),
    ])),
]
