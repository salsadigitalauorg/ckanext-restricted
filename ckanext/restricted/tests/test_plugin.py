"""Tests for plugin.py."""
import json

from ckanext.restricted.plugin import RestrictedPlugin


def test_restricted_urls_not_indexed():
    resources = [
        {'url': 'https://open.example.com/a.csv', 'restricted': '{"level": "public"}'},
        {'url': 'https://secret.example.com/b.csv', 'restricted': '{"level": "same_organization"}'},
        {'url': 'https://legacy.example.com/c.csv'},
    ]
    pkg_dict = {'validated_data_dict': json.dumps({'resources': resources}),
                'res_url': [r['url'] for r in resources]}
    pkg_dict = RestrictedPlugin().before_dataset_index(pkg_dict)
    assert pkg_dict['res_url'] == ['https://open.example.com/a.csv', 'https://legacy.example.com/c.csv']
