# version 1.0.1
from f5.bigip import ManagementRoot
import click
import tenacity
import requests
import json
import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class CannotRetrieveTokenException(Exception):
    pass


@click.command()
@click.option('--servers', required=True)
@click.option('--password', required=True)
@click.option('--bucket', required=True)
@click.option('--region', required=True)
def cli(servers, password, bucket, region):
    servers = servers.split(',')
    click.echo(f'Start BigIP backup at {time.strftime("%c")}')
    for s in servers:
        click.echo(f'Server: {s}')
        login_url = f'https://{s}/mgmt/shared/authn/login'
        base_request_url = f'https://{s}/mgmt/tm/task/sys/ucs'

        login_details = {
            "username": 'admin',
            "password": password,
            "login_url": login_url,
            "base_request_url": base_request_url
        }

        token = get_token(login_details)
        token_id = create_backup(login_details, token, s)
        change_state(login_details, token, token_id)
        while check_status(login_details, token, token_id):
            time.sleep(5)
            pass
        backup_to_s3(s, password, bucket, region)
    click.echo(f'\nFinish BigIp backup to S3 at {time.strftime("%c")}.')


@tenacity.retry(
    stop=tenacity.stop_after_attempt(2),
    wait=tenacity.wait_fixed(60),
    retry=(
        tenacity.retry_if_exception_type(RuntimeError)
    )
)
def backup_to_s3(s, password, bucket, region):
    mgmt = ManagementRoot(s, 'admin', password)
    file_name = f'{s}.ucs'
    mgmt.shared.file_transfer.uploads.upload_file('/template/s3put.sh')
    s3put = '/var/config/rest/downloads/s3put.sh'
    ddir = '/var/tmp/scripts'
    ch_command = f'chmod +x {s3put}; mkdir {ddir}; mv {s3put} {ddir}  '
    click.echo(ch_command)
    mgmt.tm.util.bash.exec_cmd(
        'run',
        utilCmdArgs=f'-c "{ch_command}"'
    )
    backup_command = \
        f'{ddir}/s3put.sh {bucket} /var/local/ucs/{file_name} {region}'
    click.echo(backup_command)
    status = mgmt.tm.util.bash.exec_cmd(
        'run',
        utilCmdArgs=f'-c "{backup_command}"'
    )
    if '204' in f'{status.raw.get("commandResult")}':
        click.echo(f'Backup was Upload to S3 bucket {bucket}')
    else:
        raise RuntimeError(
            click.echo(f'Fail to copy {file_name} to S3 bucket {bucket}'),
            click.echo(f'Status: {status.raw.get("commandResult")}')
        )


def get_token(login_details):
    payload = {'username': login_details['username'],
               'password': login_details['password'],
               "loginProvidername": "tmos"}
    headers = {
        'Content-Type': 'application/json',
    }

    response = requests.post(
        url=login_details['login_url'],
        headers=headers,
        data=json.dumps(payload),
        verify=False
    )

    if response.status_code == 200:
        a = response.json()
        token = a.get('token')
        return token['token']

    raise CannotRetrieveTokenException("Cannot retrieve token")


def create_backup(login_details, token, server):
    click.echo(f'Start to Create Backup on bigip server {server}')
    headers = {
        'Content-Type': 'application/json',
        'X-F5-Auth-Token': token
    }
    data = {
        "command": "save",
        "name": server
    }
    response = requests.post(url=login_details['base_request_url'],
                             headers=headers,
                             data=json.dumps(data),
                             verify=False)

    d = json.loads(response.text)
    task_id = d['_taskId']
    time.sleep(1)
    return task_id


def change_state(login_details, token, task_id):
    if task_id:
        headers = {
            'Content-Type': 'application/json',
            'X-F5-Auth-Token': token
        }
        data = {"_taskState": "VALIDATING"}
        url = f"{login_details['base_request_url']}/{task_id}"
        requests.put(url=url,
                     headers=headers,
                     data=json.dumps(data),
                     verify=False)


def check_status(login_details, token, task_id):
    headers = {
        'Content-Type': 'application/json',
        'X-F5-Auth-Token': token
    }
    url_task = f"{login_details['base_request_url']}/{task_id}"
    response = requests.get(url=url_task, headers=headers, verify=False)
    if response.status_code == 200:
        d = json.loads(response.text)
        task_state = d['_taskState']

        if task_state == 'COMPLETED':
            url_result = f"{login_details['base_request_url']}/{task_id}/result"
            requests.get(url=url_result, headers=headers, verify=False)
            requests.delete(url=url_task, headers=headers, verify=False)
            return False
        else:
            return True


if __name__ == '__main__':
    cli(auto_envvar_prefix='F5_BACKUP')
