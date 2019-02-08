from collections import defaultdict
import boto3
import os

# Report should be run using restricted IAM Role.
# IAM 'ec2report' credentials should be stored as a boto3 profile (example: ~/.aws/credentials)
os.environ['AWS_PROFILE'] = 'ec2report'   # Define which profile to connect with
session = boto3.Session(profile_name='ec2report')   # Create a boto3 session using the defined profile

# Obtain all publicly available regions
region_list = session.get_available_regions('ec2')

ec2data = defaultdict()

for region in region_list:
    ec2 = boto3.resource('ec2', region)   # Print a delimiter to identify the current region
    instances = ec2.instances.filter(   # Filter the list of returned instances
        Filters=[
            {'Name': 'instance-state-name', 'Values': ['stopped', 'running']},    # Return only instances that are stopped or running
        ]
    )
    for instance in instances:
        name = ''   # Initialise the variable : name
        state = ''    # Initialise the variable : state
        tags = instance.tags

        if tags is not None:
            for tag in tags:
                key = tag['Key']
                if str.lower(key) == 'name':    # Check for any tags with a value of Name or name
                    name = tag['Value']   # Set name variable to be equal to the value of the Name/name tag
                if str.lower(key) == 'owner':
                    owner = tag['Value']
                if str.lower(key) == 'project':
                    project = tag['Value']
        else:   # Set default values if Tag is not present
            name = "NOT SET"
            owner = "NOT SET"
            project = "NOT SET"

        if instance.state['Name'] is not None:
            state = instance.state['Name']
        else:
            state = 'NOT SET'

        if instance.instance_lifecycle is not None:
            lifecycle = instance.instance_lifecycle
        else:
            lifecycle = 'Scheduled'

        if instance.private_ip_address is not None:
            private_ip = instance.private_ip_address
        else:
            private_ip = 'NONE'

        if instance.public_ip_address is not None:
            public_ip = instance.public_ip_address
        else:
            public_ip = 'NONE'

        # Add instance info to a dictionary         
        ec2data[instance.id] = { 
            'Name': name,
            'Type': instance.instance_type,
            'Lifecycle': lifecycle,
            'Owner' : owner,
            'State': state,
            'Private IP': private_ip,
            'Public IP': public_ip,
            'Launch Time': instance.launch_time
            }

attributes = ['Name', 'Type', 'Lifecycle', 'Owner', 'State', 'Private IP', 'Public IP', 'Launch Time']
for instance_id, instance in ec2data.items():
    for key in attributes:
        print("{0}: {1}".format(key, instance[key]))
    print("------")
