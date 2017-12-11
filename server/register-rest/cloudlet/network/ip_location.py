#!/usr/bin/env python
#
# Cloudlet Infrastructure for Mobile Computing
#
#   Author: Kiryong Ha <krha@cmu.edu>
#
#   Copyright (C) 2011-2013 Carnegie Mellon University
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import urllib
import pprint
import math
import os


class IPGelocationError(Exception):
    pass


class Location(object):
    def __init__(self, properties):
        for k, v in properties.iteritems():
            setattr(self, k.lower(), v)

        if 'longitude' not in self.__dict__:
            raise IPGelocationError("Need longitude attribute")
        if 'latitude' not in self.__dict__:
            raise IPGelocationError("Need latitude attribute")
        if type(self['longitude']) != float:
            raise IPGelocationError("Longitude attribute is not float")
        if type(self['latitude']) != float:
            raise IPGelocationError("Latitude attribute is not float")

    def __str__(self):
        ret = pprint.pformat(self.__dict__)
        return ret

    def __getitem__(self, item):
        return self.__dict__[item]

    def __sub__(self, other):
        if type(other) != Location:
            raise IPGelocationError("Invalid class")
        lat1, lon1 = self.latitude, self.longitude
        lat2, lon2 = other.latitude, other.longitudej
        return geo_distance(lat1, lon1, lat2, lon2)


def geo_distance(lat1, lon1, lat2, lon2):
    radius = 6371  # km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = radius * c
    return distance


def _is_float(str):
    try:
        float(str)
        return True
    except ValueError:
        return False


class IPLocation(object):
    CUR_PATH = os.path.dirname(os.path.abspath(__file__))
    MAXMIND_DB_PATH = os.path.join(CUR_PATH, "db", "GeoLiteCity.dat")

    def __init__(self):
        self.maxmind_db_path = IPLocation.MAXMIND_DB_PATH

    def ip2location(self, ip_address):
        # get getlocation from http://maxmind.com/
        import pygeoip
        if self.maxmind_db_path is None or os.path.exists(self.maxmind_db_path) is False:
            raise IPGelocationError(
                "Cannot find maxmind DB at : %s" % self.maxmind_db_path)
        self.gi = pygeoip.GeoIP(self.maxmind_db_path, pygeoip.MEMORY_CACHE)
        ret_dict = self.gi.record_by_addr(ip_address)
        if ret_dict:
            ret_dict['ip_address'] = ip_address
            return Location(ret_dict)
        else:
            return None

    def ip2location_hostip(self, ip_address):
        # get geolocation from http://www.hostip.info/
        query_str = "http://api.hostip.info/get_html.php?ip=%s&position=true" % (
            ip_address)
        response = urllib.urlopen(query_str).read().strip()
        ret_items = [item.strip()
                     for item in response.split("\n") if len(item) > 0]
        ret_dict = dict()
        for item in ret_items:
            key, value = item.split(":")
            key = key.strip()
            value = value.strip()
            if _is_float(value):
                ret_dict[key] = float(value)
            else:
                ret_dict[key] = value

        return Location(ret_dict)


if __name__ == "__main__":
    iploc = IPLocation(maxmind_db_path="./GeoLiteCity.dat")
    print(iploc.ip2location("128.2.210.197"))
    print(iploc.ip2location("1.2.210.147"))
    print(iploc.ip2location("192.2.233.197"))
    print(iploc.ip2location("143.248.233.197"))

    loc1 = iploc.ip2location("128.2.210.197")
    loc2 = iploc.ip2location("129.2.233.1")
    loc3 = iploc.ip2location("143.248.233.197")
    print "disktance between (%s) and (%s) is %f km" % (loc1.city, loc2.city, loc1 - loc2)
    print "disktance between (%s) and (%s) is %f km" % (loc1.city, loc3.city, loc1 - loc3)
