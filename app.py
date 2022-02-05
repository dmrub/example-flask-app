#!/usr/bin/env python3
import os
import pprint

import requests
from flask import (
    Flask,
    Response,
    current_app,
    jsonify,
    render_template,
    request,
    url_for,
)

from flask_reverse_proxy import ReverseProxied

app = Flask(__name__, instance_relative_config=True)
app.wsgi_app = ReverseProxied(app.wsgi_app)
logger = app.logger

# Load default config and override config from an environment variable
app.config.update(
    dict(
        SECRET_KEY=os.urandom(24),
        LOG_FILE=os.path.join(app.instance_path, "example-app.log"),
        FILE_FOLDER=os.path.join(app.instance_path, "files"),
        PORT=os.environ.get("PORT", 5000),
        MAX_CONTENT_LENGTH=100 * 1024 * 1024,  # Maximal 100 Mb for files
    )
)
app.config.from_envvar("EXAMPLE_APP_SETTINGS", silent=True)

HTTP_OK = 200
HTTP_BAD_REQUEST = 400
HTTP_NOT_FOUND = 404
HTTP_INTERNAL_SERVER_ERROR = 500
HTTP_NOT_IMPLEMENTED = 501


def error_response(message, status_code=HTTP_INTERNAL_SERVER_ERROR):
    response = jsonify({"message": message})
    response.status_code = status_code
    return response


def bad_request(message):
    return error_response(message=message, status_code=HTTP_BAD_REQUEST)


def not_found(message):
    return error_response(message=message, status_code=HTTP_NOT_FOUND)


def not_implemented(message):
    return error_response(message=message, status_code=HTTP_NOT_IMPLEMENTED)


@app.errorhandler(requests.exceptions.ConnectionError)
def on_request_exception(error):
    return error_response(
        message=str(error), status_code=HTTP_INTERNAL_SERVER_ERROR
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/debug/flask/", methods=["GET"])
def debug_flask():
    import urllib

    output = ["Rules:"]
    for rule in current_app.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        if rule.methods:
            methods = ",".join(rule.methods)
        else:
            methods = "GET"
        url = url_for(rule.endpoint, **options)
        line = urllib.parse.unquote(
            "{:50s} {:20s} {}".format(rule.endpoint, methods, url)
        )
        output.append(line)

    output.append("")
    output.append("Request environment:")
    for k, v in request.environ.items():
        output.append("{0}: {1}".format(k, pprint.pformat(v, depth=5)))

    output.append("")
    output.append("Request vars:")
    output.append("request.path: {}".format(request.path))
    output.append("request.full_path: {}".format(request.full_path))
    output.append("request.script_root: {}".format(request.script_root))
    output.append("request.url: {}".format(request.url))
    output.append("request.base_url: {}".format(request.base_url))
    output.append("request.host_url: {}".format(request.host_url))
    output.append("request.url_root: {}".format(request.url_root))
    output.append("")

    return Response("\n".join(output), mimetype="text/plain")


if __name__ == "__main__":
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    print("Running on port {}".format(port))
    app.run(host="0.0.0.0", port=port)
