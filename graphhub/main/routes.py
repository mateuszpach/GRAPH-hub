from flask import render_template, request, Blueprint
from flask_login import current_user
from sqlalchemy import func

from graphhub import db
from graphhub.models import Graph, Tag, User, Comment, Like

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/browse")
def browse():
    page = request.args.get('page', 1, type=int)
    filter_tags = request.args.getlist('filter_tags', None)
    filter_user = request.args.get('filter_user', None, type=int)
    order = request.args.get('order_by', 'date_added_desc')

    comments = db.session.query(Comment.graph_id, func.count(Comment.id).label('nr_comments')). \
        group_by(Comment.graph_id).subquery()

    likes = db.session.query(Like.graph_id, func.count(Like.id).label('nr_likes')). \
        group_by(Like.graph_id).subquery()

    if current_user.is_authenticated:
        liked = db.session.query(Like.graph_id, func.count(Like.id).label('liked')). \
            group_by(Like.graph_id).filter_by(user_id=current_user.id).subquery()
    else:
        liked = db.session.query(Like.graph_id, func.count(Like.id).label('liked')). \
            group_by(Like.graph_id).filter_by(user_id=None).subquery()

    graphs = db.session.query(Graph, comments.c.nr_comments, likes.c.nr_likes, liked.c.liked). \
        outerjoin(comments, Graph.id == comments.c.graph_id). \
        outerjoin(likes, Graph.id == likes.c.graph_id). \
        outerjoin(liked, Graph.id == liked.c.graph_id)

    if filter_tags:
        graphs = graphs.filter(Graph.tags.any(Tag.text.in_(filter_tags)))

    if filter_user:
        graphs = graphs.filter(Graph.user_id == filter_user)

    if order == 'date_added_desc':
        graphs = graphs.order_by(Graph.date_added.desc())
    elif order == 'date_added_asc':
        graphs = graphs.order_by(Graph.date_added.asc())
    elif order == 'likes_desc':
        graphs = graphs.order_by(likes.c.nr_likes.desc())
    elif order == 'likes_asc':
        graphs = graphs.order_by(likes.c.nr_likes.asc())

    graphs = graphs.paginate(page=page, per_page=5)

    tags = Tag.query.with_entities(Tag.text).distinct(Tag.text).order_by(Tag.text.asc()).all()

    users = User.query.with_entities(User.id, User.username).order_by(User.username.asc()).all()

    return render_template('browse.html', graphs=graphs, tags=tags, users=users,
                           order_by=order, filter_tags=filter_tags, filter_user=filter_user)


@main.route("/about")
def about():
    return render_template('about.html', title='About')
