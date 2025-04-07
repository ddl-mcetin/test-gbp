import subprocess

# This is a sample Python/Flask app showing Domino's App publishing functionality.
# You can publish an app by clicking on "Publish" and selecting "App" in your
# quick-start project.

import json
import flask
from flask import request, redirect, url_for
import numpy as np
from domino_data.datasets import DatasetClient

import os

class ReverseProxied(object):
  def __init__(self, app):
      self.app = app
  def __call__(self, environ, start_response):
      script_name = os.environ.get('DOMINO_RUN_HOST_PATH', '')
      if script_name:
          environ['SCRIPT_NAME'] = script_name
          path_info = environ['PATH_INFO']
          if path_info.startswith(script_name):
              environ['PATH_INFO'] = path_info[len(script_name):]
      # Setting wsgi.url_scheme from Headers set by proxy before app
      scheme = environ.get('HTTP_X_SCHEME', 'https')
      if scheme:
        environ['wsgi.url_scheme'] = scheme
      return self.app(environ, start_response)

app = flask.Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)

# Homepage which uses a template file
@app.route('/')
def index_page():
  return "hello world"

# Sample redirect using url_for
@app.route('/redirect_test')
def redirect_test():
  return redirect( url_for('another_page') )

# Sample return string instead of using template file
@app.route('/another_page')
def another_page():
  msg = "You made it with redirect( url_for('another_page') )." + \
        "A call to flask's url_for('index_page') returns " + url_for('index_page') + "."
  return msg

@app.route('/random')
@app.route('/random/<int:n>')
def random(n = 100):
    try:
        random_numbers = list(np.random.random(n))
        return json.dumps(random_numbers)
    except Exception as e:
        app.logger.error(f"Error in random route: {e}")
        return f"Error generating random numbers: {e}", 500

@app.route('/datasets')
def datasets():
    auth_header = request.headers.get('Authorization', None)
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[len("Bearer "):]
    else:
        return jsonify({"error": "Missing or invalid Authorization header"}), 401

    try:
        dataset = DatasetClient(token=token).get_dataset("dataset-AppDatasets-67eb46120aa8e17a5ffc1ff0")
        file_objects = dataset.list_files()
        
        # Convert custom file objects to dicts (adjust fields as needed)
        file_list = [
            {
                "path": f.path,
                "size": f.size,
                "last_modified": str(f.last_modified)
            }
            for f in file_objects
        ]
        
        return jsonify(file_list)
    except Exception as e:
        # Log the error as needed
        app.logger.error("Error accessing dataset: %s", e)
        return jsonify({"error": "Access denied. " 
                        "Please ensure your credentials have the required permissions."}), 403

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')