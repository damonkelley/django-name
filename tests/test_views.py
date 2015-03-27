import pytest
import json

from django.core.urlresolvers import reverse


@pytest.mark.django_db
def test_entry_detail_returns_ok(client, name_fixture):
    response = client.get(
        reverse('name_entry_detail', args=[name_fixture.name_id]))
    assert 200 == response.status_code


@pytest.mark.django_db
def test_entry_detail_returns_gone(client, name_fixture):
    name_fixture.record_status = 1
    name_fixture.save()
    response = client.get(
        reverse('name_entry_detail', args=[name_fixture.name_id]))
    assert 410 == response.status_code


@pytest.mark.django_db
def test_entry_detail_returns_not_found(client, name_fixture):
    name_fixture.record_status = 2
    name_fixture.save()
    response = client.get(
        reverse('name_entry_detail', args=[name_fixture.name_id]))
    assert 404 == response.status_code


@pytest.mark.django_db
def test_merged_entry_detail_returns_ok(client, merged_name_fixtures):
    merged, primary = merged_name_fixtures
    response = client.get(
        reverse('name_entry_detail', args=[primary.name_id]))
    assert 200 == response.status_code


@pytest.mark.django_db
def test_merged_entry_detail_returns_redirect(client, merged_name_fixtures):
    merged, primary = merged_name_fixtures
    response = client.get(
        reverse('name_entry_detail', args=[merged.name_id]))
    assert 302 == response.status_code


@pytest.mark.django_db
def test_mads_serialize_returns_ok(client, name_fixture):
    response = client.get(
        reverse('name_mads_serialize', args=[name_fixture.name_id]))
    assert 200 == response.status_code


@pytest.mark.django_db
def test_label_returns_redirected(client, name_fixture):
    response = client.get(
        reverse('name_label', args=[name_fixture.name]))
    assert 302 == response.status_code


@pytest.mark.django_db
def test_label_returns_not_found_without_query(client):
    response = client.get(
        reverse('name_label', args=['']))
    assert 404 == response.status_code
    assert 'No matching term found' not in response.content


@pytest.mark.django_db
def test_label_returns_not_found_with_query(client):
    response = client.get(
        reverse('name_label', args=['&&&&&&&&']))
    assert 404 == response.status_code
    assert 'No matching term found' in response.content


@pytest.mark.django_db
def test_export(client, name_fixture):
    response = client.get(reverse('name_export'))
    assert 200 == response.status_code


def test_opensearch(client):
    response = client.get(reverse('name_opensearch'))
    assert 200 == response.status_code


@pytest.mark.django_db
def test_feed(client):
    response = client.get(reverse('name_feed'))
    assert 200 == response.status_code


def test_about(client):
    response = client.get(reverse('name_about'))
    assert 200 == response.status_code


@pytest.mark.django_db
def test_stats_returns_ok(client, name_fixture):
    response = client.get(reverse('name_stats'))
    assert 200 == response.status_code


# FIXME: This should not throw a 500
@pytest.mark.xfail
@pytest.mark.django_db
def test_stats_returns_ok_with_no_names(client):
    response = client.get(reverse('name_stats'))
    assert 200 == response.status_code


@pytest.mark.django_db
def test_get_names_returns_ok(client):
    response = client.get(reverse('name_names'))
    assert 200 == response.status_code


@pytest.mark.django_db
def test_get_names_xhr_returns_ok(client):
    response = client.get(
        reverse('name_names'),
        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert 200 == response.status_code


@pytest.mark.django_db
def test_get_names_xhr_returns_only_10_names(client, twenty_name_fixtures):
    response = client.get(
        reverse('name_names'),
        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    names = json.loads(response.content)
    assert len(names) == 10


# TODO: Take another look at this. We might not need
#       Allow-Headers on every request, perhaps only ajax
# TODO: Find a way to test that the origin header is set to '*'
@pytest.mark.django_db
def test_get_names_has_cors_headers(client):
    response = client.get(reverse('name_names'))
    assert response.has_header('Access-Control-Allow-Origin')
    assert response.has_header('Access-Control-Allow-Headers')


@pytest.mark.django_db
def test_landing(client):
    response = client.get(reverse('name_landing'))
    assert 200 == response.status_code


@pytest.mark.django_db
def test_name_json_returns_ok(client, name_fixture):
    response = client.get(reverse('name_json', args=[name_fixture]))
    assert 200 == response.status_code


# FIXME: This should not return a 500
@pytest.mark.xfail
@pytest.mark.django_db
def test_name_json_handles_unknown_name(client):
    response = client.get(reverse('name_json', args=[0]))
    assert 404 == response.status_code
