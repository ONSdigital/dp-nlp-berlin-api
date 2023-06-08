from datetime import datetime
from app.config import NAMESPACE
import structlog


def configure_logging():
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(),
        ],
        context_class=structlog.threadlocal.wrap_dict(dict),
        logger_factory=structlog.stdlib.LoggerFactory(),
    )


def setup_logger():
    return structlog.get_logger(
        namespace=NAMESPACE,
        created_at=datetime.utcnow().isoformat(),
    )
