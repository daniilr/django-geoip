.. _update:

Updating GeoIP database
=======================

.. note::
    Currentrly ``django-geoip`` supports only ipgeobase.ru backend.

To update your database with fresh entries
(adds new geography and completely replaces all IpRegions with fresh ones)::

    python manage.py geoip_update

If you wish to clear all geodata prior the sync
(deletes all Cities, Regions, Countries and IpRanges)::

    python manage.py geoip_update --clear

