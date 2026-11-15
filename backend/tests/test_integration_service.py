
import pytest

from app.services.integration_service import (
    validate_gis_input,
    validate_similarity_input,
    prepare_integration_response
)


def test_valid_gis_input():
    data = {"sample_location": "Jezero Crater"}
    assert validate_gis_input(data) is True


def test_invalid_gis_input():
    with pytest.raises(ValueError):
        validate_gis_input([])


def test_valid_similarity_input():
    data = {"matches": []}
    assert validate_similarity_input(data) is True


def test_invalid_similarity_input():
    with pytest.raises(ValueError):
        validate_similarity_input(None)


def test_prepare_integration_response():
    gis_data = {"sample_location": "Jezero Crater"}
    similarity_data = {"matches": []}

    response = prepare_integration_response(
        gis_data,
        similarity_data
    )

    assert response["status"] == "success"
    assert response["gis_data"] == gis_data
    assert response["similarity_data"] == similarity_data


def test_empty_gis_data():
    with pytest.raises(ValueError):
        validate_gis_input({})


def test_empty_similarity_data():
    with pytest.raises(ValueError):
        validate_similarity_input({})
