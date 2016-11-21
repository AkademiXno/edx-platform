"""
Helper functions to access and update the id and type
used in event tracking.
"""
from uuid import uuid4
from request_cache import get_cache


def get_user_action_id():
    """
    Retrieves the current tracking root id from the request
    cache.
    """
    return get_cache('grade_tracking').get('tracking_root_id', None)


def get_user_action_type():
    """
    Retrieves the current tracking root type from the request
    cache.
    """
    return get_cache('grade_tracking').get('tracking_root_type', None)


def create_new_user_action_id():
    """
    Generates a new UUID and stores it in the request cache
    as the tracking root id.
    """
    new_id = uuid4()
    get_cache('grade_tracking')['tracking_root_id'] = new_id
    return new_id


def set_user_action_type(root_type):
    """
    Takes a string and stores it in the request cache
    as the tracking root type.
    """
    get_cache('grade_tracking')['tracking_root_type'] = root_type
