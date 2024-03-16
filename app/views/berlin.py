import traceback

from flask import Blueprint, jsonify, request

from app.logger import format_errors, logger
from app.models import LocationModel, MatchModel
from app.store import get_db

from berlin import Location
from Levenshtein import distance

db = get_db()

berlin_blueprint = Blueprint("berlin", __name__)


MIN_FRACTION_PLACENAME_MATCH = 0.75

def qualify_match(loc: Location, query: str) -> bool:
    start, end = loc.get_offset()
    if not (start < end) or start > len(query):
        return False
    text = query[start:end]
    phrase = loc.get_names()[0]
    words = loc.get_names() + loc.words

    if not phrase or not text:
        return False
    for word in words:
        if (
            len(word) / len(phrase) > MIN_FRACTION_PLACENAME_MATCH and
            distance(text, word) < 3
        ):
            return True
    return False


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
    query = request.args.get("q")
    state = request.args.get("state") or "gb"
    limit = request.args.get("limit", type=int) or 10
    lev_distance = request.args.get("lev_distance", type=int) or 2
    try:
        try:
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
            if qualify_match(loc, query)
        ]

        locations = {"query": query, "matches": matches}
        if matches:
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
