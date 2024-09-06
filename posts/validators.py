from rest_framework import serializers


def validate_title_no_hello(value):
    if value:
        return value
    else:
        return None
