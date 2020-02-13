"""
Copyright (C) 2005-2015 Splunk Inc. All Rights Reserved.

Commonly used design partten for python user, includes:
  - singleton (Decorator function used to build singleton)
"""

from functools import wraps


def singleton(class_):
    """
    Singleton decoorator function.
    """
    instances = {}

    @wraps(class_)
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance
