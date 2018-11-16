from flask import jsonify, request, url_for, make_response
from app import app
from .models import Feed
from .models import FeedSchema
from .models import Post
from .models import PostSchema
from .spider import get_today_all_data
from app import db
import time
from flask_cors import CORS, cross_origin
import requests
import json

result = []

CORS(app, support_credentials=True)


# 兼容线上服务器和本地服务器数据结构
def getResult(query_result):
    if isinstance(query_result, list):
        result = query_result
    else:
        result = query_result.data
    return result


# 首页视图路由
@app.route('/')
def index():
    return '<h1>公众号数据采集系统后台</h1>'


# 获取所有的公众号
@app.route("/api/all/feed", methods=['get'])
def get_all_feed():
    query_obj = Feed.query.order_by(Feed.id).all()
    feed_schema = FeedSchema(many=True)
    return jsonify({
        'code': 1,
        'data': getResult(feed_schema.dump(query_obj)),
        'msg': '公众号列表'
    })


# 获取分页的公众号
@app.route("/api/feed", methods=['get'])
def get_feed_list():
    page = request.args.get('page', 1, type=int)
    query_obj = Feed.query.order_by(Feed.id).paginate(page=page, per_page=10)
    feed_schema = FeedSchema(many=True)
    query_result = {
        'feed_list': getResult(feed_schema.dump(query_obj.items)),
        'total_pages': query_obj.pages,
        'total': query_obj.total,
        'page': query_obj.page
    }
    return jsonify({
        'code': 1,
        'data': query_result,
        'msg': '公众号列表'
    })


# 获取某公众号的所有文章
@app.route("/api/<wx_id>/post")
def get_post_list(wx_id):
    page = request.args.get('page', 1, type=int)
    is_marked = request.args.get('is_marked')
    query_obj = Post.query.filter_by(wx_id=wx_id, is_marked=is_marked).paginate(page=page, per_page=10)
    post_schema = PostSchema(many=True)
    query_result = {
        'post_list': getResult(post_schema.dump(query_obj.items)),
        'total_pages': query_obj.pages,
        'total': query_obj.total,
        'page': query_obj.page
    }
    return jsonify({
        'code': 1,
        'data': query_result,
        'msg': '公众文章列表'
    })


# 获取所有文章
@app.route("/api/post")
def get_all_post_list():
    page = request.args.get('page', 1, type=int)
    is_marked = request.args.get('is_marked')
    query_obj = Post.query.filter_by(is_marked=is_marked).paginate(page=page, per_page=10)
    post_schema = PostSchema(many=True)
    query_result = {
        'post_list': getResult(post_schema.dump(query_obj.items)),
        'total_pages': query_obj.pages,
        'total': query_obj.total,
        'page': query_obj.page
    }
    return jsonify({
        'code': 1,
        'data': query_result,
        'msg': '所有文章列表'
    })


# 添加公众号
@app.route("/api/feed", methods=['POST'])
def add_feed():
    retdict = {
        'code': 1,
        'data': {},
        'msg': '添加公众号成功'}

    response = make_response(json.dumps(retdict))
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Origin'] = request.environ['HTTP_ORIGIN']
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'
    feed_data = Feed(wx_id=request.form['wx_id'],
                     wx_title=request.form['wx_title'],
                     scraping_time=request.form['scraping_time'])
    db.session.add_all([feed_data])
    db.session.commit()
    return response


# 获取公众号基本信息
@app.route('/api/feed/<int:feed_id>', methods=['GET'])
def get_feed(feed_id):
    print(feed_id)
    data = Feed.query.filter_by(id=feed_id).first()
    feed_schema = FeedSchema()
    return jsonify({
        'code': 1,
        'data': feed_schema.dump(data),
        'msg': '公众号信息详情'
    })


# 修改公众号基本信息
@app.route('/api/feed/<int:feed_id>', methods=['POST'])
def update_feed(feed_id):
    retdict = {
        'code': 1,
        'data': {},
        'msg': '编辑公众号成功'}
    response = make_response(json.dumps(retdict))
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Origin'] = request.environ['HTTP_ORIGIN']
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'
    # print(data)
    update = Feed.query.filter_by(id=feed_id).first()
    update.wx_id = request.form['wx_id']
    update.wx_title = request.form['wx_title']
    update.scraping_time = request.form['scraping_time']
    db.session.commit()
    return response


# 获取文章基本信息
@app.route('/api/post/<int:post_id>', methods=['GET'])
def get_post(post_id):
    print(post_id)
    data = Post.query.filter_by(id=post_id).first()
    post_schema = PostSchema()
    return jsonify({
        'code': 1,
        'data': post_schema.dump(data),
        'msg': '文章详情'
    })


# 将文章标记并保存到研究中
@app.route('/api/post/<int:post_id>/mark', methods=['POST'])
def update_post_marked(post_id):
    retdict = {
        'code': 1,
        'data': {},
        'msg': '文章标记成功'}
    response = make_response(json.dumps(retdict))
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Origin'] = request.environ['HTTP_ORIGIN']
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'
    # print(data)
    update = Post.query.filter_by(id=post_id).first()
    update.is_marked = request.form['is_marked']
    db.session.commit()
    post_schema = PostSchema()
    data = post_schema.dump(update)
    # print(data)
    r = requests.post('https://www.aikepler.com/api/wx/research', data=data)
    print(r.text)
    response_text = json.loads(r.text)
    if response_text['code'] == 1:
        print(response_text['msg'])
    else:
        print(response_text['msg'])
    return response


# 修改文章的标签
@app.route('/api/post/<int:post_id>/tag', methods=['POST'])
def update_post_keywords(post_id):
    retdict = {
        'code': 1,
        'data': {},
        'msg': '修改关键词成功'}
    response = make_response(json.dumps(retdict))
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Origin'] = request.environ['HTTP_ORIGIN']
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'
    # print(data)
    update = Post.query.filter_by(id=post_id).first()
    update.keywords = request.form['keywords']
    db.session.commit()
    return response


# 删除公众号
@app.route('/api/feed/<int:feed_id>', methods=['DELETE'])
def delete_feed(feed_id):
    delete = Feed.query.filter_by(id=feed_id).first()
    db.session.delete(delete)
    db.session.commit()
    return jsonify({
        'code': 1,
        'data': '',
        'msg': '删除成功！'})


# 爬取特定日期的数据
@app.route('/api/data')
def get_data():
    feed_list = request.args.get('feed_list').split(',')
    update_date = request.args.get('update_date')
    get_today_all_data(feed_list, update_date)
    return jsonify({
        'code': 1,
        'data': '',
        'msg': '获取数据成功！'})
