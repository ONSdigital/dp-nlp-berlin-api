import traceback

from flask import Blueprint, jsonify, request

from app.logger import format_errors, logger
from app.models import LocationModel, MatchModel
from app.store import get_db

db = get_db()

berlin_blueprint = Blueprint("berlin", __name__)


@berlin_blueprint.route("/berlin/code/<key>", methods=["GET"])
def berlin_code(key):
    try:
        loc = db.retrieve(key)

    except Exception as e:
        logger.error(
            event="error retrieving key from database ",
            errors=format_errors(e, trace=traceback.format_exc()),
        )

        return jsonify({"key": key, "error": "Not found"}), 404

    location = LocationModel.from_location(loc, db)
    return jsonify(location.to_json()), 200


@berlin_blueprint.route("/berlin/search", methods=["GET"])
def berlin_search():
    q = request.args.get("q")
    state = request.args.get("state") or "gb"
    limit = request.args.get("limit", type=int) or 10
    lev_distance = request.args.get("lev_distance", type=int) or 2

    if not q:
        logger.info(
            event="no query provided",
        )
        return (
            jsonify({"error": "q is a required parameter"}),
            400,
        )

    try:
        query = ""
        longerQuery = False
        if len(q) > 30:
            longerQuery = True
            # Find the first space before 30th character
            if (loc := q[:30][::-1].find(" ")) > 0:
                query = q[: 29 - loc]
            # ...or take up to the 30th character if none.
            else:
                query = q[:30]
        else:
            query = q
                
        try:
            logger.info(
                event="searching database for query",
                data={"query":query}
            )
            result = db.query(query, state=state, limit=limit, lev_distance=lev_distance)
        except BaseException as e:
            logger.error(
                event="error querying the database (rust) ",
                errors=format_errors(e, trace=traceback.format_exc()),
            )
            return (
                jsonify({"error": "error querying the database"}),
                500,
            )

        matches = [
            {
                "loc": LocationModel.from_location(loc, db).to_json(),
                "scores": MatchModel.from_location(loc).to_json(),
            }
            for loc in result
        ]

        locations = {"query": q, "matches": matches}
        if matches and not longerQuery:
            start_idx = matches[0]["scores"]["offset"][0]
            end_idx = matches[0]["scores"]["offset"][1]
            query = query[:start_idx] + query[end_idx:]
            locations = {"query": query, "matches": matches}

        return jsonify(locations), 200

    except Exception as e:
        logger.error(
            event="error querying the database",
            errors=format_errors(e, trace=traceback.format_exc()),
        )
        return (
            jsonify({"error": "error querying the database"}),
            500,
        )
