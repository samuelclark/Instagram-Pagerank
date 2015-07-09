import datetime
from instagram.client import InstagramAPI
from api_settings import *


class InstagramSearch:
    """
        this class wraps the instagram api functionality
    """
    def __init__(self, access_token=None):
        if not access_token:
            access_token=ACCESS_TOKEN
        self.api = InstagramAPI(access_token=access_token)
        self.api_calls = 0

    def tag_recent_media(self, tag_name, pages=1, count=25):
        """
            Searches instagram api for tag_name and returns serialized dictionary of media
        """
        duplicates = 0
        tag_recent_media = {}
        max_id = None
        # could try except this to prevent timeouts
        for pg in range(pages):
            new_media = 0
            print "searching for {0} with id {1} on loop {2}".format(tag_name, max_id, pg)
            media, callback = self.api.tag_recent_media(count, max_id, tag_name=tag_name)
            self.api_calls += 1
            for each in media:
                if each.id in tag_recent_media:
                    duplicates += 1
                else:
                    new_media += 1
                    tag_recent_media[each.id] = serialize_media(each)
            print "pg {0} --> found {1} new media".format(pg, new_media)
            print callback
            max_id = int(callback.split("&")[-1].split("=")[1])
        print "query: {0} --> retrieved {1} items --> {2} duplicates".format(tag_name, len(tag_recent_media), duplicates)
        return tag_recent_media

    def tag_search(self, tag):
        return self.api.tag_search(tag)


def serialize_date(d, sformat="%y-%m-%dT%H:%M:%S"):
    """
        helper function to serialize datetime object <d> to <sformat>
    """
    if isinstance(d, datetime.datetime):
        d = d.strftime(sformat)
    return d


def serialize_list(values):
    """
        serializes values
        <values> - a list of class objectss
    """
    serialized = []
    for each in values:
        each = check_date_user(each.__dict__)
        # unpack tags
        if 'name' in each:
            each = each['name']
        serialized.append(each)

    return serialized


def check_date_user(value):
    """
        serializes date and user object from sublists
        <value> - dictionary of media info
    """
    if 'created_at' in value:
        value['created_at'] = serialize_date(value['created_at'])
    if 'user' in value:
        value['user'] = value['user'].__dict__
    return value


def serialize_media(media):
    """
        converts result of tag_recent_media to json serializable format
    """
    clean_media = {}
    lists_to_serialize = ['tags', 'comments', 'likes']
    keys_to_serialize = ['caption', 'user']
    dates = ['created_time', 'created_at']
    for key, value in media.__dict__.iteritems():
        if value:
            if key in lists_to_serialize:
                value = serialize_list(value)
            elif key in keys_to_serialize:
                value = check_date_user(value.__dict__)
            elif key in dates:
                value = serialize_date(value)
            elif key == 'images':
                value = value['standard_resolution'].__dict__['url']
            elif key == 'location':
                value = value.__dict__['point']
                if value:
                    value = value.__dict__
                else:
                    value ='no location'
        clean_media[key] = value
    return clean_media
