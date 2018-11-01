import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


# g is a special object that is unique for each request. (每次请求都会新创建一个对象)
# It is used to store data that might be accessed by multiple functions during the request (用于在请求期间在多个函数之间共享数据).
# The connection is stored and reused instead of creating a new connection if get_db is called a second time in the same request .
# (保存下数据库的连接，这样在同一请求就不会多次创建数据库的连接).

# current_app is another special object that points to the Flask application handling the request.
# Since you used an application factory, there is no application object when writing the rest of your code.
# get_db will be called when the application has been created and is handling a request, so current_app can be used.
# current_app 是一个全局应用上下文，表示的是当前运行的 flask 实例。  在__init__.py 中我们是通过工厂方法 create_app 创建了 flask 实例 app.
# 我们在其他文件中是获取不到这个 app变量的,所以我们通过访问 current_app 的方式，来得到我们想要的全局数据，比如数据库连接 URL。

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )

        g.db.row_factory = sqlite3.Row
    #  sqlite3.Row tells the connection to return rows that behave like dicts. This allows accessing the columns by name.
    #  相当于 pymysql.cursors.DictCursor

    return g.db


def close_db(e=None):
    # g设置变量，直接用.XX 就行，删除要用pop
    db = g.pop('db', None)

    if db is not None:  # if a connection was created by checking if g.db was set
        db.close()


def init_db():
    db = get_db()

    # 在 flask 中打开文件的方式，路径都是相对于 flaskr 的，你配置了 instance_relative_config=True
    # open_resource() opens a file relative to the flaskr package, which is useful since you won’t necessarily know
    # where that location is when deploying the application later.
    # get_db returns a database connection, which is used to execute the commands read from the file.
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


# click.command() defines a command line command called init-db that calls the init_db function
# and shows a success message to the user. You can read Command Line Interface to learn more about writing commands.
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


# 将 close_db 和 init_db_command 函数注册到 flask 实例中，让flask 知道他们的存在。注意，因为采用了工厂方法，我们采用了完全不同的获取
# app 实例的方式。 上面是通过 current_app，现在是设置一个函数，通过在另一段代码中调用
# The close_db and init_db_command functions need to be registered with the application instance
# However, since you’re using a factory function, that instance isn’t available when writing the functions.
# Instead, write a function that takes an application and does the registration.
def init_app(app):
    app.teardown_appcontext(close_db)
    # tells Flask to call that function when cleaning up after returning the response.
    # 返回响应的时候回调

    app.cli.add_command(init_db_command)
    # adds a new command that can be called with the flask command.
    # 添加到 flask 命令行
