DATABASE = {
    'name': 'dormitory',
    'engine': 'peewee.MySQLDatabase',
    'host': 'fybmain.com',
    'user': 'dormitory',
    'passwd': 'cOUP0Guy',
}

PASSWORD_HASH_SALT = "DORMITORY_HASH_SALT_DEBUG"
SERVER_SECRET_KEY = "DORMITORY_SERVER_SECRET_KEY_DEBUG"
LOGIN_EXPIRE_TIME = 30*24*60*60

AUTH_TOKEN_HTTP_HEADER = "X-AUTH-TOKEN"
