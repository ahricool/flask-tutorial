# Instead of creating a Flask instance globally, you will create it inside a function.
# This function is known as the application factory. Any configuration, registration,
# and other setup the application needs will happen inside the function, then the application will be returned.

# The __init__.py serves double duty:
# it will contain the application factory,
# and it tells Python that the flaskr directory should be treated as a package
#  __init__ 是包的标志.

import os
from flask import Flask


# create a Flask instance inside a function as application factory
def create_app(test_config=None):
    # 创建 flask 实例，其他所有的东西都是注册在这个实例上面的，为这个实例服务。
    app = Flask(__name__, instance_relative_config=True)
    # __name__应该是用来初始化 app.instance_path 的
    # 如果是直接运行的 __name__ 返回的是 __main__ ,如果不是 __name__返回的是文件名字（不含 py）
    # instance_relative_config=True tells the app that configuration files are relative to the instance folder.

    # sets some default configuration that the app will use
    app.config.from_mapping(
        # SECRET_KEY is used by Flask and extensions to keep data safe.
        # It’s set to 'dev' to provide a convenient value during development,
        # but it should be overridden with a random value when deploying.
        SECRET_KEY='dev',
        # 设置sqlite路径
        # app.instance_path 以后会配置
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    # 覆盖默认的配置
    # overrides the default configurativalues taken from the config.py file
    # in the instance folder if it exists.
    # For example, when deploying, this can be used to set a real SECRET_KEY.

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)

    else:
        app.config.from_pyfile(test_config)

    # 路径要自己建
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 直接在flask 实例上注册
    @app.route('/hello')
    def hello():
        return 'Hello,World！'

    # 因为采用了 create_app 工厂方法，其他函数无法感知 flask 实例 app ,所以这里设置了调用。
    from . import db
    db.init_app(app)

    # 同样的原因，需要在这里注册 Blueprint
    # The authentication Blueprint will have views to register new users and to login and logout
    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    # Import and register the blueprint from the factory using app.register_blueprint().
    app.register_blueprint(blog.bp)

    '''
    app.add_url_rule() associates the endpoint name 'index' with the / url 
    so that url_for('index') or url_for('blog.index') will both work, 
    generating the same / URL either way.
    '''
    # index view 的路径设置的是 / 但是 endpoint 依然是 blog.index
    # 对于 authentication views 是不友好的，这里将 endpoint index 和 / 关联起来
    # index 和 blog.index 都可以访问的 view
    app.add_url_rule('/', endpoint='index')

    '''
    In another application you might give the blog blueprint a url_prefix 
    and define a separate index view in the application factory, similar to the hello view. 
    Then the index and blog.index endpoints and URLs would be different.
    '''

    return app
