import pytest
import uuid

from calm.dsl.cli.main import get_api_client
from calm.dsl.cli.constants import RUNLOG
from tests.api_interface.test_runbooks.test_files.http_task import HTTPTaskWithoutAuth
from utils import upload_runbook, poll_run_script_output


class TestPlayground:
    @pytest.mark.runbook
    @pytest.mark.regression
    def test_http_playground(self):
        """ test_http_playground """

        client = get_api_client()
        rb_name = "test_runbook_" + str(uuid.uuid4())[-10:]

        rb = upload_runbook(client, rb_name, HTTPTaskWithoutAuth)
        rb_state = rb["status"]["state"]
        rb_uuid = rb["metadata"]["uuid"]
        print(">> Runbook state: {}".format(rb_state))
        assert rb_state == "ACTIVE"
        assert rb_name == rb["spec"]["name"]
        assert rb_name == rb["metadata"]["name"]

        # endpoints generated by this runbook
        endpoint_list = rb['spec']['resources'].get('endpoint_definition_list', [])

        # running the playground task
        print("\n>>Playground on http task")

        payload = dict()
        payload['metadata'] = rb['metadata']
        payload['api_version'] = rb['api_version']
        payload['spec'] = dict()
        payload['spec']['provider_operation_payload'] = "{\"method\":\"GET\"}"
        payload['spec']['attrs'] = {'script_type': 'REST'}
        payload['spec']['targetDetails'] = rb['spec']['resources']['default_target_reference']

        res, err = client.runbook.run_script(rb_uuid, payload)
        if err:
            pytest.fail("[{}] - {}".format(err["code"], err["error"]))

        response = res.json()
        request_id = response["status"]["request_id"]
        trl_id = response["status"]["trl_id"]

        # polling till runbook run gets to input state
        state = poll_run_script_output(client, rb_uuid, trl_id, request_id, RUNLOG.TERMINAL_STATES)

        print(">> RUN SCRIPT STATE: {}".format(state))
        assert state == RUNLOG.STATUS.SUCCESS

        # delete the runbook
        res, err = client.runbook.delete(rb_uuid)
        if err:
            pytest.fail("[{}] - {}".format(err["code"], err["error"]))
        else:
            print("runbook {} deleted".format(rb_name))

        # delete endpoints generated by this test
        for endpoint in endpoint_list:
            _, err = client.endpoint.delete(endpoint["uuid"])
            if err:
                pytest.fail("[{}] - {}".format(err["code"], err["error"]))
