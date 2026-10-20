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
