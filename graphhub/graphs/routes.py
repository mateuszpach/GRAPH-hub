from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint, send_file, jsonify)
from flask_login import current_user, login_required

from graphhub import db
from graphhub.graphs.forms import GraphForm, CommentForm
from graphhub.graphs.utils import save_project
from graphhub.models import Graph, Tag, Comment, Like

graphs = Blueprint('graphs', __name__)


@graphs.route("/graph/new", methods=['GET', 'POST'])
@login_required
def new_graph():
    form = GraphForm()
    if form.validate_on_submit():
        project_file = save_project(form.project_file.data)
        graph = Graph(name=form.name.data,
                      description=form.description.data,
                      author=current_user,
                      project_file=project_file)
        for tag_text in form.tags.data.split(','):
            tag = Tag.query.filter_by(text=tag_text).first()
            if not tag:
                tag = Tag(text=tag_text)
                db.session.add(tag)
            graph.tags.append(tag)
        db.session.add(graph)
        db.session.commit()
        flash('Your graph has been added!', 'success')
        return redirect(url_for('graphs.graph', graph_id=graph.id))
    return render_template('new_graph.html', title='New Graph',
                           form=form, legend='New Graph')


@graphs.route("/graph/<int:graph_id>", methods=['GET', 'POST'])
def graph(graph_id):
    graph = Graph.query.get_or_404(graph_id)
    form = CommentForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            comment = Comment(text=form.text.data,
                              graph_id=graph.id,
                              author=current_user)
            db.session.add(comment)
            db.session.commit()
            flash('Your comment has been added!', 'success')
            return redirect(url_for('graphs.graph', graph_id=graph.id))
        else:
            flash('You must be logged in to comment!', 'danger')
            return redirect(url_for('graphs.graph', graph_id=graph.id))
    comments = Comment.query.filter_by(graph_id=graph.id)
    nr_comments = comments.count()
    comments = comments.all()
    nr_likes = Like.query.filter_by(graph_id=graph.id).count()
    if current_user.is_authenticated:
        liked = Like.query.filter_by(graph_id=graph.id).filter_by(user_id=current_user.id).count()
    else:
        liked = 0
    return render_template('graph.html', title=graph.name, graph=graph, comments=comments, nr_comments=nr_comments,
                           nr_likes=nr_likes, liked=liked, form=form)


@graphs.route("/graph/<int:graph_id>/download")
def download_graph(graph_id):
    graph = Graph.query.get_or_404(graph_id)
    graph.downloads = graph.downloads + 1
    db.session.commit()
    return send_file(graph.project_file, as_attachment=True,
                     attachment_filename=graph.name + '.gmom')


@graphs.route("/graph/<int:graph_id>/update", methods=['GET', 'POST'])
@login_required
def update_graph(graph_id):
    graph = Graph.query.get_or_404(graph_id)
    if graph.author != current_user:
        abort(403)
    form = GraphForm()
    if form.validate_on_submit():
        graph.name = form.name.data
        graph.description = form.description.data
        graph.project_file = save_project(form.project_file.data)
        graph.tags = []
        for tag_text in form.tags.data.split(','):
            tag = Tag.query.filter_by(text=tag_text).first()
            if not tag:
                tag = Tag(text=tag_text)
                db.session.add(tag)
            graph.tags.append(tag)
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('graphs.graph', graph_id=graph.id))
    elif request.method == 'GET':
        form.name.data = graph.name
        form.description.data = graph.description
    return render_template('new_graph.html', title='Update graph',
                           form=form, legend='Update graph')


@graphs.route("/graph/<int:graph_id>/delete", methods=['POST'])
@login_required
def delete_graph(graph_id):
    graph = Graph.query.get_or_404(graph_id)
    if graph.author != current_user:
        abort(403)
    db.session.query(Comment).filter_by(graph_id=graph.id).delete()
    db.session.query(Like).filter_by(graph_id=graph.id).delete()
    db.session.delete(graph)
    db.session.commit()
    flash('Your graph has been deleted!', 'success')
    return redirect(url_for('main.browse'))


@graphs.route("/graph/like", methods=['GET', 'POST'])
def like_graph():
    if current_user.is_authenticated:
        graph_id = request.args.get('graph_id', None, type=int)
        Graph.query.get_or_404(graph_id)
        like = Like.query.filter_by(author=current_user).filter_by(graph_id=graph_id)
        if like.count() == 0:
            like = Like(graph_id=graph_id, author=current_user)
            db.session.add(like)
            db.session.commit()
            return jsonify(status=200, action='like')
        else:
            like.delete()
            db.session.commit()
        return jsonify(status=200, action='dislike')
    return jsonify(status=403)
