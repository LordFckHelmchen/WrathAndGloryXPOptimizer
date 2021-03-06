import json
import logging.config
import sys

from flask import Flask, request, abort, Request

import xpOptimizer

# Configure logging on WSGI server-defined stream with default config
# from https://flask.palletsprojects.com/en/1.1.x/logging/#basic-configuration
logging.config.dictConfig(
    {
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            }
        },
        'handlers': {
            'wsgi': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://flask.logging.wsgi_errors_stream',
                'formatter': 'default'
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    }
)
app = Flask(__name__)

MAX_ARGUMENT_COUNT_FOR_LOGGING = 10


def request_to_str(request: Request, prefix: str = ">>> ", suffix: str = " <<<"):
    return f"\n{prefix}HEADER{suffix}\n" \
           f"{request.headers}" \
           f"{prefix}ARGUMENTS{suffix}\n" \
           f"len_args: {len(request.args)}\n" \
           f"args_keys: {tuple(request.args.keys()) if len(request.args) <= MAX_ARGUMENT_COUNT_FOR_LOGGING else '<TOO MANY>'}\n"


@app.route('/optimize_xp')
def optimize_xp():
    if "target_values" not in request.args:
        app.logger.info(f"Request without 'target_values' received. {request_to_str(request)}")
        abort(400)

    if len(request.args) != 1:
        app.logger.warning(f"Unexpected number of arguments received. {request_to_str(request)}")
        # Ignore additional inputs

    if not xpOptimizer.is_valid_target_values_dict(json.loads(request.args["target_values"])):
        app.logger.info(f"Invalid target values dict received: '{request.args['target_values']}'")
        abort(400)

    # noinspection PyBroadException
    try:
        return dict(xpOptimizer.optimize_xp(json.loads(request.args["target_values"])))
    except:
        app.logger.error(f"Optimizer error for target value dict {request.args['target_values']}: "
                         f"{sys.exc_info()[0]}: {sys.exc_info()[1]}")
        abort(500)
