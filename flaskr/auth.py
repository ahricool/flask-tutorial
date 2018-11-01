import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

# 以下这两个函数用在对密码的处理上。
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

'''
Blueprint 相当于一个集合，集合的元素是 view。 不同于我们在 最简单的 flask 应用中做的那样，直接把 view 注册到 app.
我们先把 view 以及其他代码注册到 Blueprint,然后把 Blueprint 注册到 app.

A Blueprint is a way to organize a group of related views and other code.
Rather than registering views and other code directly with an application,
they are registered with a blueprint. 
Then the blueprint is registered with the application when it is available in the factory function.
'''

'''
This creates a Blueprint named 'auth'. Like the application object, the blueprint needs to know where it’s defined, 
so __name__ is passed as the second argument.
The url_prefix will be prepended to all the URLs associated with the blueprint.
'''

bp = Blueprint('auth', __name__, url_prefix='/auth')


# @bp.route associates the URL /register with the register view function.
# When Flask receives a request to /auth/register,
# it will call the register view and use the return value as the response.
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        # request.form is a special type of dict mapping submitted form keys and values.
        username = request.form['username']
        password = request.form['password']
        db = get_db()

        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        # Validate that username is not already registered by querying the database
        # and checking if a result is returned. db.execute takes a SQL query with ? placeholders for any user input,
        # and a tuple of values to replace the placeholders with.
        # The database library will take care of escaping the values
        # so you are not vulnerable to a SQL injection attack.
        # 数据库的包将会检查用户输出的合法性，确保不会轻易的遭到的 sql 注入。

        # fetchone() returns one row from the query.
        # If the query returned no results, it returns None.
        # Later, fetchall() is used, which returns a list of all results.
        # fetchone() 和 fetchall() 在查询结果为空的时候时候差别还是很大的。
        # fetchone() 返回的是 None. fetchall() 返回的是()

        elif db.execute(
                'SELECT id FROM user WHERE username=? ', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        # If validation succeeds, insert the new user data into the database.
        # For security, passwords should never be stored in the database directly.
        # Instead, generate_password_hash() is used to securely hash the password, and that hash is stored.
        # Since this query modifies data, db.commit() needs to be called afterwards to save the changes.

        if error is None:
            db.execute(
                'INSERT INTO user (username,password) VALUES (?,?)',
                (username, generate_password_hash(password))

            )
            db.commit()

            # After storing the user, they are redirected to the login page.
            # url_for() generates the URL for the login view based on its name.
            # 'auth.login' 是 view 的名字而不是 url
            # This is preferable to writing the URL directly as it allows you to change the URL later
            # without changing all code that links to it.
            # redirect() generates a redirect response to the generated URL.
            return redirect(url_for('auth.login'))

        # If validation fails, the error is shown to the user.
        # flash() stores messages that can be retrieved when rendering the template
        # YOU CAN USE GET_FLASHED_MESSAGES() IN THE TAMPLATES TO GET THE ERROR MESSGAE.

        # Flashes a message to the next request.
        # In order to remove the flashed message from the session and to display it to the user,
        # the template has to call get_flashed_messages().
        # 模板调用 get_flashed_messages() 就会获得 error
        flash(error)
    # 这个 return 是在 if request.method=='POST' 外面的，当用 GET 方法，或者 POST 提交有错误就会 return
    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # 将查询结果保存在 user 里面
        user = db.execute(
            'SELECT * FROM user WHERE username =?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'

        # the hash function is generate_password_hash in register view
        # check_password_hash() hashes the submitted password in the same way
        # as the stored hash and securely compares them. If they match, the password is valid.
        # 数据库中的 password 的字段将会保存加密方式和盐 pbkdf2:sha1:1000$X97hPa3g$252c0cca000c3674b8ef7a2b8ecd409695aac370
        # 因为盐值是随机的，所以就算是相同的密码，生成的哈希值也不会是一样的

        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        # session is a dict that stores data across requests.
        # When validation succeeds, the user’s id is stored in a new session.
        # The data is stored in a cookie that is sent to the browser,
        # and the browser then sends it back with subsequent requests.
        # Flask securely signs the data so that it can’t be tampered with.
        # 在http 连接中保持 session 的有效性，通过加密的 cookie 来保持。

        if error is None:
            session.clear()
            # 只是设置一下 user_id
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


# bp.before_app_request() registers a function that runs before the view function, no matter what URL is requested.
# load_logged_in_user checks if a user id is stored in the session and gets that user’s data from the database,
# storing it on g.user, which lasts for the length of the request.
# If there is no user id, or if the id doesn’t exist, g.user will be None.
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None

    else:
        # 这里才是根据 session 来设置用户信息
        # g 在每次请求的时候都会重置，所有每次其请求g 都不一样
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id=?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# Creating, editing, and deleting blog posts will require a user to be logged in.
# A decorator（装饰器）can be used to check this for each view it’s applied to.
# 确保访问某些页面之前，你已经登入了，这里是检查了一下 g.user
# 因为 login_required 是一个装饰器，所以是在 load_logged_in_user 调用之后调用的。
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

# This decorator returns a new view function that wraps the original view it’s applied to.
# The new function checks if a user is loaded and redirects to the login page otherwise.
# If a user is loaded the original view is called and continues normally.
#  You’ll use this decorator when writing the blog views.

# The url_for() function generates the URL to a view based on a name and arguments.
# The name associated with a view is also called the endpoint,
# and by default it’s the same as the name of the view function.
# endpoint 指的是一个 view 名，这个 view名 关联着一个 view ，默认的情况下 view名和 view 的函数名相同。
# 而 url_for() 是需要一个 endpoint 或者 URL 作为参数的。endpoint 还需要 blueprint 作为前缀。

# When using a blueprint, the name of the blueprint is prepended to the name of the function,
# so the endpoint for the login function you wrote above is 'auth.login'
# because you added it to the 'auth' blueprint.
