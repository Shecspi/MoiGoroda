import os

from storages.backends.s3boto3 import S3Boto3Storage


class UsersCityPhotoStorage(S3Boto3Storage):
    bucket_name = os.getenv('AWS_USERS_CITY_PHOTOS_BUCKET_NAME')
    region_name = os.getenv('AWS_USERS_CITY_PHOTOS_REGION_NAME')
    querystring_auth = True
    querystring_expire = int(os.getenv('AWS_USERS_CITY_PHOTOS_URL_EXPIRE_SECONDS', '120'))
    default_acl = None
    file_overwrite = False
