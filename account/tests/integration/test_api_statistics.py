from typing import Any

import pytest


@pytest.mark.integration
@pytest.mark.django_db
def test_personal_visited_cities_overview_returns_zero_ranks_without_data(
    client: Any, django_user_model: Any
) -> None:
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    client.force_login(user)

    response = client.get('/api/account/stats/visited_cities/overview/')

    assert response.status_code == 200
    data = response.json()
    assert data['unique_visited_cities']['count'] == 0
    assert data['unique_visited_cities_rank'] == 0
    assert data['total_visited_cities_visits']['count'] == 0
    assert data['total_visited_cities_visits_rank'] == 0
