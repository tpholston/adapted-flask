import os

def get_connect_url():
    return os.environ.get("AWS_DATABASE_URL")
