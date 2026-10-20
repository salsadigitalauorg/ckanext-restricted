"""Tests for auth.py."""
from ckanext.restricted import auth


def test_public_resource_in_private_dataset_denied(monkeypatch):
    monkeypatch.setattr(auth.authz, 'is_authorized', lambda name, context, data_dict: {'success': False})
    resource = {'id': 'res-1', 'package_id': 'pkg-1', 'restricted': '{"level": "public"}'}
    assert auth.restricted_resource_show({}, {'resource': resource})['success'] is False
