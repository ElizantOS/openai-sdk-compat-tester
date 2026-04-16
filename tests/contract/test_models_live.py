def test_models_list(live_client):
    response = live_client.models.list()

    assert len(response.data) > 0
