#!/usr/bin/env python3

from flask import Flask, request, abort

import base64
import plistlib
import json
import requests
import logging

from urllib.parse import urljoin


def create_app(test_config=None):
    """
    To initialise the app, load a list of profiles to be installed according to MicroMDM blueprints.
    """

    app = Flask(__name__)
    app.logger.setLevel(logging.INFO)

    app.config.from_prefixed_env(prefix='MICROMDM')

    # set up a session for requests to MicroMDM API
    app.req_session = requests.Session()
    app.req_session.auth = requests.auth.HTTPBasicAuth('micromdm', app.config['API_KEY'])

    # fetch list of blueprints and profile IDs contained
    app.profiles = dict()
    r = app.req_session.post(urljoin(app.config['API_URL'], '/v1/blueprints'), json={})
    for blueprint in r.json()['blueprints']:
        app.logger.info(f'blueprint {blueprint["uuid"]} [{blueprint["name"]}] lists the following profiles:')
        for profile in blueprint["profile_ids"]:
            app.logger.info(f' - {profile}')
            app.profiles[profile] = None

    # fetch profiles to get the expected UUIDs
    app.logger.info('profile details:')
    for profile_id in app.profiles.keys():
        r = app.req_session.post(urljoin(app.config['API_URL'], '/v1/profiles'), json={ "id": profile_id })
        for profile in r.json()['profiles']:
            if profile['Identifier'] == profile_id:
                payload = plistlib.loads(base64.b64decode(profile['Mobileconfig']))
                app.profiles[profile_id] = {
                    "payload": profile['Mobileconfig'],
                    "uuid": payload["PayloadUUID"],
                }
                app.logger.info(f' - {profile_id} [{payload["PayloadDescription"]}] has UUID {payload["PayloadUUID"]}')

    @app.route('/webhook', methods=['POST'])
    def webhook():
        """
        The webhook checks whether all profiles are installed in the correct version (based on the profile's UUID)
        """
        if 'acknowledge_event' in request.json and 'raw_payload' in request.json['acknowledge_event']:
            plist = base64.b64decode(request.json['acknowledge_event']['raw_payload'])
            payload = plistlib.loads(plist)
            if 'ProfileList' in payload:
                app.logger.info(f'checking ProfileList from {payload["UDID"]}:')
                installed = { i["PayloadIdentifier"]: i["PayloadUUID"] for i in payload["ProfileList"] }
                for profile_id in app.profiles.keys():
                    if profile_id in installed:
                        if installed[profile_id] == app.profiles[profile_id]['uuid']:
                            app.logger.info(f' - {profile_id} already installed, UUID is correct')
                        else:
                            app.logger.info(f' - {profile_id} already installed, UUID mismatch: {installed[profile_id]} [installed] != {app.profiles[profile_id]["uuid"]} [required]')
                    else:
                        app.logger.info(f' - {profile_id} is not installed')
            else:
                app.logger.debug(f'response from {payload["UDID"]} is not a ProfileList, ignoring')
            return ('', 204)
        else:
            app.logger.debug(f'unexpectedly formatted payload')
            abort(400)

    return app

if __name__ == '__main__':
    create_app().run(host="0.0.0.0", port=8000, debug=True)

