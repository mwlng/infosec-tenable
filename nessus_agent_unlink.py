#!/usr/bin/env python

import sys
import json

from botocore.exceptions import ClientError

from boto3wrapper.clients import EC2Client
from tenableio import TenableAgent


def list_aws_tenable_agents(t_access_key, t_secret_key,
                            aws_accounts, status, t_group_name=None):
    agents = []
    with TenableAgent(
            access_key=t_access_key,
            secret_key=t_secret_key) as ta:
        for agent in ta.get_agents():
            if 'aws_account_id' in agent:
                if agent['aws_account_id'] in aws_accounts and agent['status'].lower() == status:
                    group = agent['groups'][0]['name'] if 'groups' in agent else "null"
                    if t_group_name and group == t_group_name:
                        agents.append({
                            'aws_account_id': agent['aws_account_id'],
                            'aws_instance_id': agent['aws_instance_id'],
                            'id': agent['id'],
                            'name': agent['name'],
                            'group': group
                        })
                    else:
                        agents.append({
                            'aws_account_id': agent['aws_account_id'],
                            'aws_instance_id': agent['aws_instance_id'],
                            'id': agent['id'],
                            'name': agent['name'],
                            'group': group
                        })
    return agents


def unlink_aws_tenable_agents(t_access_key, t_secret_key, agents):
    with TenableAgent(
            access_key=t_access_key,
            secret_key=t_secret_key) as ta:
        ta.unlink_agents(agents)


def unlink_agents_by_name(t_access_key, t_secret_key, name, agents):
    unlink_agents = []
    for agent in agents:
        if agent['name'] == name:
            unlink_agents.append(agent['id'])
    # Unmark below line to output agents which will be unlinked
    # print(unlink_agents)
    unlink_aws_tenable_agents(t_access_key, t_secret_key, unlink_agents)


def main():
    # AWS account's ID
    aws_accounts = ['524xxxxxxxxx']

    tenable_access_key = "xxxxxxxxxx"
    tenable_secret_key = "xxxxxxxxxx"

    agents = list_aws_tenable_agents(
        tenable_access_key, tenable_secret_key, aws_accounts, 'on', 'NYC_AWS_Dev')

    stale_agents = []
    with EC2Client() as ec2:
        for agent in agents:
            instance_ids = [agent['aws_instance_id']]
            try:
                statuses = ec2.describe_instance_status(instance_ids,
                                                        include_all_instances=True)['InstanceStatuses']
                if statuses:
                    if statuses[0]['InstanceState']['Name'] == 'terminated':
                        stale_agents.append(agent)
                else:
                    stale_agents.append(agent)
            except ClientError as e:
                if e.response['Error']['Code'] == "InvalidInstanceID.NotFound":
                    stale_agents.append(agent)

    # Unmark below line to output all stale agents
    # print(stale_agents)

    # Unmark below line to unlink all stale agents
    #unlink_aws_tenable_agents(tenable_access_key, tenable_secret_key, agents)

    # Unlink one of stale agents by ec2 instance host name
    unlink_agents_by_name(tenable_access_key, tenable_secret_key,
                          'ip-10-64-216-4', stale_agents)

    return 0


if __name__ == "__main__":
    sys.exit(main())
