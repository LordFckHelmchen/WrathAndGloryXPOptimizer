import json

from flask import Flask, request, abort

import xpOptimizer
app = Flask(__name__)


@app.route('/optimize_xp')
def optimize_xp():
    if "target_values" not in request.args \
            or len(request.args) != 1 \
            or not xpOptimizer.is_valid_target_values_dict(json.loads(request.args["target_values"])):
        abort(400)

    return dict(xpOptimizer.optimize_xp(json.loads(request.args["target_values"])))
