from django.conf.urls import include, url
from django.contrib import admin

from trips.views import TripListCreateView, TripRetrieveView, BookTripView
from users.views import (RegisterUser, LoginUser, LogoutUser, GetUpdateUser,
    VerifyUserEmail, ChangePassword, RequestPasswordReset, ResetPassword)


urlpatterns = [
    url(r'^api/v1/', include([
        url(r'^user/register/?$', RegisterUser.as_view(), name='register'),
        url(r'^user/login/?$', LoginUser.as_view(), name='login'),
        url(r'^user/logout/?$', LogoutUser.as_view(), name='logout'),
        url(r'^user/change-password/?$', ChangePassword.as_view(), name='change_pass'),
        url(r'^user/request-password/?$', RequestPasswordReset.as_view(), name='request_pass'),
        url(r'^user/reset-password/?$', ResetPassword.as_view(), name='reset_pass'),
        url(r'^user/verify_email/?$', VerifyUserEmail.as_view(), name='verify_email'),
        url(r'^user/?$', GetUpdateUser.as_view(), name='get_update_user'),

        url(r'^trip/?$', TripListCreateView.as_view(), name='trip_list_create'),
        url(r'^trip/(?P<pk>[0-9]+)/?$', TripRetrieveView.as_view(), name='trip_retrieve'),
        url(r'^trip/book/(?P<pk>[0-9]+)/?$', BookTripView.as_view(), name='book_trip'),
    ])),
]
