from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort

# 引入 login_required 装饰器，部分页面要做登入认证
from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

'''
Unlike the auth blueprint, the blog blueprint does not have a url_prefix. 
So the index view will be at /, the create view at /create, and so on.
'''


# index的 endpoint 依然是blog.index
@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id,title,body,created,author_id,username'
        ' FROM post p JOIN user u ON p.author_id=uid'
        ' ORDER BY created DESC'
    ).fetchall()

    # 这里将 posts 变量作为 posts 返回，这样在模板中也可以使用 post 变量。
    return render_template('blog/index.html', posts=posts)


# A user must be logged in to visit these views, otherwise they will be redirected to the login page.
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)

        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title,body,author_id)'
                'VALUES (?,?,?)', (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


# 一个确认权限的过程，title id 要和 uid 匹配
def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id,title,body ,created, author_id,username'
        '  FROM post p JOIN user u ON p.author_id=u.id'
        '  WHERE p.id= ?', (id,)
    ).fetchone()

    # abort 会抛出一个特定的异常,这个异常会返回一个 HTTP 的状态码.
    # abort() will raise a special exception that returns an HTTP status code.
    # It takes an optional message to show with the error, otherwise a default message is used.
    # 404 means “Not Found”, and 403 means “Forbidden”.
    # (401 means “Unauthorized”, but you redirect to the login page instead of returning that status.)
    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    # The check_author argument is defined so that the function can be used to get a post without checking the author.
    # This would be useful if you wrote a view to show an individual post on a page,
    # where the user doesn’t matter because they’re not modifying the post.
    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


# Unlike the views you’ve written so far, the update function takes an argument, id.
# That corresponds to the <int:id> in the route.
# A real URL will look like /1/update.
# Flask will capture the 1, ensure it’s an int, and pass it as the id argument.
# If you don’t specify int: and instead do <id>, it will be a string.
# To generate a URL to the update page, url_for() needs to be passed the id
# so it knows what to fill in: url_for('blog.update', id=post['id']). This is also in the index.html file above.
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title=?,body=?'
                '  WHERE id=?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id=?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
