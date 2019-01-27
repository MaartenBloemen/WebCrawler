from flask import Flask, render_template

from controllers.job_controller import job_controller

PREFIX = '/api/v1'

app = Flask(__name__, template_folder='templates', static_folder='static')

app.config['JSON_SORT_KEYS'] = False
app.secret_key = 'crawler'

app.register_blueprint(job_controller, url_prefix=PREFIX)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8405)
