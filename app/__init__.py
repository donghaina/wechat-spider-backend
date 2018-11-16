from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_apscheduler import APScheduler
import time

app = Flask(__name__)
app.config.from_pyfile('./config.py')

result = []
db = SQLAlchemy(app)
ma = Marshmallow(app)

from app import models
from app import api
from app import spider


def get_all_feed():
    spider.get_all_feed_post_list()


scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.add_job(id='get_all_feed', func=get_all_feed, trigger='cron', day='1-31', hour='11', minute='0')
scheduler.init_app(app)
scheduler.start()