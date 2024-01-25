from market import app
from flask_wtf.csrf import CSRFProtect
from flask_http_middleware import MiddlewareManager
from market.metricmiddlesware import MetricsMiddleware

#Checks if the run.py file has executed directly and not imported
if __name__ == '__main__':
    csrf = CSRFProtect(app)
    csrf.init_app(app)

    app.wsgi_app = MiddlewareManager(app)
    app.wsgi_app.add_middleware(MetricsMiddleware)

    app.run(debug=True)



