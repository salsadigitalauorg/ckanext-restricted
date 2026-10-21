"""Tests for action.py."""
import pytest

from ckanext.restricted import action


@pytest.fixture
def resource():
    return {'id': 'res-1', 'package_id': 'pkg-1', 'url': 'https://source.example.com/data.csv',
            'restricted': '{"level": "same_organization", "allowed_users": ""}'}


def _mock_access(monkeypatch, can_read, can_edit):
    monkeypatch.setattr(action.auth, 'restricted_resource_show', lambda context, data_dict: {'success': can_read})
    monkeypatch.setattr(action.authz, 'is_authorized', lambda name, context, data_dict: {'success': can_edit})
    monkeypatch.setattr(action.logic, 'restricted_get_username_from_context', lambda context: 'someone')


def test_url_hidden_without_access(monkeypatch, resource):
    _mock_access(monkeypatch, can_read=False, can_edit=False)
    [result] = action._restricted_resource_list_hide_fields({}, [resource])
    assert result['url'] == ''
    assert resource['url'] == 'https://source.example.com/data.csv'


def test_url_kept_with_access(monkeypatch, resource):
    _mock_access(monkeypatch, can_read=True, can_edit=False)
    [result] = action._restricted_resource_list_hide_fields({}, [resource])
    assert result['url'] == 'https://source.example.com/data.csv'


def test_xloader_original_url_hidden_without_access(monkeypatch, resource):
    _mock_access(monkeypatch, can_read=False, can_edit=False)
    resource['original_url'] = resource['url']
    [result] = action._restricted_resource_list_hide_fields({}, [resource])
    assert 'original_url' not in result


def test_activity_stores_no_restricted_urls(monkeypatch, resource):
    public = {'id': 'res-2', 'url': 'https://open.example.com/a.csv'}
    activity = {'data': {'package': {'resources': [dict(resource, original_url=resource['url']), public]}}}
    stored = []
    action.restricted_activity_create(lambda context, data_dict: stored.append(data_dict), {}, activity)
    restricted_res, public_res = stored[0]['data']['package']['resources']
    assert restricted_res['url'] == '' and 'original_url' not in restricted_res
    assert public_res['url'] == 'https://open.example.com/a.csv'


def test_current_package_list_hides_urls(monkeypatch, resource):
    _mock_access(monkeypatch, can_read=False, can_edit=False)
    monkeypatch.setattr(action, 'current_package_list_with_resources', lambda context, data_dict: [{'resources': [resource]}])
    [package] = action.restricted_current_package_list_with_resources({}, {})
    assert package['resources'][0]['url'] == ''
