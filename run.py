from market import app
from flask_wtf.csrf import CSRFProtect
from flask_http_middleware import MiddlewareManager
from market.middlewares import MetricsMiddleware

#Checks if the run.py file has executed directly and not imported
if __name__ == '__main__':
    csrf = CSRFProtect(app)
    csrf.init_app(app)

    app.run(debug=True)



