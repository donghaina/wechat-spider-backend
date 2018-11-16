from datetime import timedelta

DEBUG = True
SECRET_KEY = 'horizon'
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://spider:7ujm<KI*9ol.@www.aikepler.com:3306/wechat_spider'
SEND_FILE_MAX_AGE_DEFAULT = timedelta(seconds=1)
