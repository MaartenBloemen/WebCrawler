from flask import Blueprint, jsonify

job_controller = Blueprint('job_controller', __name__)

jobs = {}


@job_controller.route('/jobs', methods=['GET'])
def get_jobs():
    return jsonify({'jobs': list(jobs.keys())})
