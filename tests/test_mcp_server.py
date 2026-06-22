import pytest

from mcp_servers.recipient_directory import server


def test_list_recipients_exposes_seed_directory():
    recipients = server.list_recipients()

    assert recipients
    assert any(recipient["recipient_id"] == "rcp_harbor_house" for recipient in recipients)
    assert all("contact_value" not in recipient for recipient in recipients)


def test_search_recipients_filters_by_category_capacity_and_distance():
    matches = server.search_recipients(["prepared_meal"], needed_capacity_meals=100, max_distance_miles=4.0)

    assert matches
    assert all(match["capacity_meals"] >= 100 for match in matches)
    assert all(match["distance_miles_demo"] <= 4.0 for match in matches)
    assert all("handling_notes" in match for match in matches)


def test_get_recipient_returns_detail_record():
    recipient = server.get_recipient("rcp_harbor_house")

    assert recipient is not None
    assert recipient["name"] == "Harbor House Shelter"
    assert recipient["contact_method"] == "simulated"


def test_get_recipient_returns_none_for_unknown_id():
    assert server.get_recipient("missing") is None


def test_build_mcp_server_has_clear_optional_dependency_error():
    if server.FastMCP is not None:
        pytest.skip("mcp package is installed in this environment")

    with pytest.raises(RuntimeError, match="mcp"):
        server.build_mcp_server()
