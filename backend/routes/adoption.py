from flask import Blueprint

# This module previously contained request-related endpoints. To avoid
# route conflicts we moved create/list/update endpoints under the
# `routes/requests.py` blueprint (registered at /requests). Keep this
# file lightweight to avoid duplicate route registration.

bp = Blueprint("adoption", __name__, url_prefix="/adoptions")
