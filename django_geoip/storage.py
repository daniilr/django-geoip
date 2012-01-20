# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from exceptions import ValueError
from django.conf import settings
from django_geoip.utils import get_class


class BaseLocationStorage(object):
    """ Base class for user location storage
    """
    value = None

    def __init__(self, request, response):
        self.request = request
        self.response = response
        self.value = self.get()

    def get(self):
        raise NotImplemented

    def set(self, location=None, force=False):
        raise NotImplemented

    def _validate_location(self, location):
        if location is None:
            return False
        return get_class(settings.GEOIP_LOCATION_MODEL).objects.filter(pk=location.id).exists()


class LocationDummyStorage(BaseLocationStorage):
    """ Fake storage for debug or when location doesn't neet to be stored
    """

    def get(self):
        return getattr(self.request, 'location', None)

    def set(self, location=None, force=False):
        return self.get()


class LocationCookieStorage(BaseLocationStorage):
    """ Class that deals with saving user location on client's side (cookies)
    """

    def get(self):
        return self.request.COOKIES.get(settings.GEOIP_COOKIE_NAME, None)

    def set(self, location=None, force=False):
        if not self._validate_location(location):
            raise ValueError
        self.value = location.id
        if force or self._should_update_cookie():
            self._do_set(self.value)

    def _do_set(self, value):
        self.response.set_cookie(
            key=settings.GEOIP_COOKIE_NAME,
            value=value,
            expires=datetime.now() + timedelta(seconds=settings.GEOIP_COOKIE_EXPIRES))

    def _should_update_cookie(self):
        # process_request never completed, don't need to update cookie
        if not hasattr(self.request, 'location'):
            return False
        # Cookie doesn't exist, we need to store it
        if settings.GEOIP_COOKIE_NAME not in self.request.COOKIES:
            return True
        # Cookie is obsolete, because we've changed it's value during request
        if str(self.get()) != str(self.value):
            return True
        return False