# coding: utf8

from __future__ import unicode_literals
import json
from ckan.lib.plugins import DefaultTranslation
import ckan.logic
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.restricted import action
from ckanext.restricted import auth
from ckanext.restricted import helpers
from ckanext.restricted import logic
from ckanext.restricted import validation
import ckanext.restricted.blueprints as blueprints

from logging import getLogger
log = getLogger(__name__)


_get_or_bust = ckan.logic.get_or_bust


class RestrictedPlugin(plugins.SingletonPlugin, DefaultTranslation):
    plugins.implements(plugins.ITranslation)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IAuthFunctions)
    # plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IBlueprint, inherit=True)
    plugins.implements(plugins.IResourceController, inherit=True)
    plugins.implements(plugins.IValidators)
    plugins.implements(plugins.IPackageController, inherit=True)


    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'restricted')

    # IActions
    def get_actions(self):
        actions = {'resource_view_list': action.restricted_resource_view_list,
                'package_show': action.restricted_package_show,
                'resource_search': action.restricted_resource_search,
                'package_search': action.restricted_package_search,
                'current_package_list_with_resources': action.restricted_current_package_list_with_resources,
                'restricted_check_access': action.restricted_check_access }
        if plugins.plugin_loaded('activity'):
            actions['activity_create'] = action.restricted_activity_create
        return actions

    # ITemplateHelpers
    def get_helpers(self):
        return {'restricted_get_user_id': helpers.restricted_get_user_id}

    # IAuthFunctions
    def get_auth_functions(self):
        return {'resource_show': auth.restricted_resource_show,
                'resource_view_show': auth.restricted_resource_show}

    # IRoutes
    # def before_map(self, map_):
    #     map_.connect(
    #         'restricted_request_access',
    #         '/dataset/{package_id}/restricted_request_access/{resource_id}',
    #         controller='ckanext.restricted.controller:RestrictedController',
    #         action='restricted_request_access_form')
    #     return map_

    # IResourceController
    def before_resource_update(self, context, current, resource):
        context['__restricted_previous_value'] = current.get('restricted')

    def after_resource_update(self, context, resource):
        previous_value = context.get('__restricted_previous_value')
        logic.restricted_notify_allowed_users(previous_value, resource)

    # IPackageController
    def before_dataset_index(self, pkg_dict):
        # package_search hides restricted URLs in results, but res_url facets and queries would still expose them.
        data_dict = json.loads(pkg_dict.get('validated_data_dict') or '{}')
        restricted_urls = {
            resource.get('url') for resource in data_dict.get('resources', [])
            if logic.restricted_get_restricted_dict(resource).get('level') != 'public'}
        if restricted_urls:
            pkg_dict['res_url'] = [url for url in pkg_dict.get('res_url', []) if url not in restricted_urls]
        return pkg_dict

    # IBlueprint
    def get_blueprint(self):
        return blueprints.get_blueprints(self.name, self.__module__)

    # IValidators
    def get_validators(self):
        return {'restricted_username_from_mail': validation.restricted_username_from_mail}
