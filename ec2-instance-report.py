import boto3
import os

# Report should be run using restricted IAM Role.
# IAM 'ec2report' credentials should be stored as a boto3 profile (example: ~/.aws/credentials)
os.environ['AWS_PROFILE'] = 'ec2report'               # Define which profile to connect with
session = boto3.Session(profile_name='ec2report')               # Create a boto3 session using the defined profile

# Obtain all publicly available regions
region_list = session.get_available_regions('ec2')

for region in region_list:
    ec2 = boto3.resource('ec2', region)               # Print a delimiter to identify the current region
    instances = ec2.instances.filter(               # Filter the list of returned instances
        Filters=[
            {'Name': 'instance-state-name', 'Values': ['stopped', 'running']},               # Return only instances that are stopped or running
        ]
    )
    for instance in instances:
        name = ''               # Initialise the variable : name
        state = ''                # Initialise the variable : state
        tags = {}               # Initialise the array : tags
        tags = instance.tags
        if tags is not None:
            for tag in tags:
                if 'Name' in tag['Key']:                # Check for any tags with a value of Name or name
                    name = tag['Value']               # Set name variable to be equal to the value of the Name/name tag
                if 'Owner' in tag['Key']:
                    owner = tag['Value']
                if 'Project' in tag['Key']:
                    project = tag['Value']
        state = instance.state['Name']
        print(region + " : " + name + " (" + instance.id + ") OWNER: " + owner  + " PROJECT: " + project + " STATE: " + state)                # Print the filtered instances formatted with the region followed by instance name
