from flask import Blueprint

from app.healthcheck import OK, Healthcheck
from app.logger import configure_logging, setup_logger

configure_logging()
logger = setup_logger()

health_check = Healthcheck(status=OK, checks=[])

health_blueprint = Blueprint("health", __name__)


@health_blueprint.route("/health", methods=["GET"])
def health():
    return health_check.to_json()
