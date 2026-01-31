"""
Logging utilities for InsightFlow.
"""
import logging
import sys
from django.conf import settings

# Configure root logger
logger = logging.getLogger('insightflow')
logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

# Formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(console_handler)

# Module-specific loggers
ingestion_logger = logging.getLogger('insightflow.ingestion')
analytics_logger = logging.getLogger('insightflow.analytics')
api_logger = logging.getLogger('insightflow.api')
