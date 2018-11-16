from app import db
from app import ma


class Feed(db.Model):
    __tablename__ = 'feed'
    id = db.Column(db.Integer, primary_key=True)
    wx_id = db.Column(db.String(50), unique=True)
    wx_title = db.Column(db.String(100), unique=True)
    scraping_time = db.Column(db.String(8))

    # scraping_time = db.Column(db.String(100))

    def __repr__(self):
        return '<Feed %r>' % self.wx_id


class FeedSchema(ma.Schema):
    class Meta:
        fields = ('id', 'wx_id', 'wx_title', 'scraping_time')
        model = Feed


class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    cover = db.Column(db.String(200))
    url = db.Column(db.String(200), unique=True, nullable=False)
    author = db.Column(db.String(50))
    wx_id = db.Column(db.String(50))
    wx_title = db.Column(db.String(50))
    wx_logo = db.Column(db.String(200))
    keywords = db.Column(db.String(200))
    abstract = db.Column(db.String(500))
    is_marked = db.Column(db.Integer)
    text = db.Column(db.Text)
    html = db.Column(db.Text)
    published_at = db.Column(db.Integer)

    def __repr__(self):
        return '<Post %r>' % self.title


class PostSchema(ma.Schema):
    class Meta:
        fields = (
            'id', 'title', 'url', 'cover', 'author', 'wx_id', 'wx_title', 'wx_logo', 'keywords', 'abstract', 'text',
            'html',
            'published_at', 'is_marked')
        model = Post
