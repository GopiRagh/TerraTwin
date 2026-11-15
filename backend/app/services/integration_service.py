
def validate_gis_input(gis_data):
    """
    Validate the basic structure of GIS output.
    Actual fields will be finalized with Member 2.
    """

    if not isinstance(gis_data, dict):
        raise ValueError("GIS data must be a JSON object")

    if not gis_data:
        raise ValueError("GIS data cannot be empty")

    return True


def validate_similarity_input(similarity_data):
    """
    Validate the basic structure of similarity output.
    Actual fields will be finalized with Member 3.
    """

    if not isinstance(similarity_data, dict):
        raise ValueError("Similarity data must be a JSON object")

    if not similarity_data:
        raise ValueError("Similarity data cannot be empty")

    return True


def prepare_integration_response(gis_data, similarity_data):
    """
    Combine GIS and similarity module outputs.
    Does not calculate or invent scientific scores.
    """

    validate_gis_input(gis_data)
    validate_similarity_input(similarity_data)

    return {
        "status": "success",
        "gis_data": gis_data,
        "similarity_data": similarity_data
    }
