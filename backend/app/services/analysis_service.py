
from uuid import uuid4
from datetime import datetime, timezone

# Temporary in-memory storage
ANALYSIS_REQUESTS = {}


def create_analysis_request(target_planet, target_location):

    analysis_id = str(uuid4())

    request = {
        "analysis_id": analysis_id,
        "target_planet": target_planet,
        "target_location": target_location,
        "status": "pending",
        "results": [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    ANALYSIS_REQUESTS[analysis_id] = request

    return request


def get_analysis_request(analysis_id):

    return ANALYSIS_REQUESTS.get(analysis_id)


def update_analysis_request(analysis_id, status, results=None):

    request = ANALYSIS_REQUESTS.get(analysis_id)

    if request is None:
        return None

    request["status"] = status

    if results is not None:
        request["results"] = results

    request["updated_at"] = datetime.now(timezone.utc).isoformat()

    return request


def get_all_analysis_requests():

    return list(ANALYSIS_REQUESTS.values())
