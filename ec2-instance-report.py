import boto3
import os

# Report should be run using restricted IAM Role.
# IAM 'ec2report' credentials should be stored as a boto3 profile (example: ~/.aws/credentials)
os.environ['AWS_PROFILE'] = "ec2report"               # Define which profile to connect with
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
        tags = {}               # Initialise the array : tags
        for tag in instance.tags:
            if (tag['Key'] == 'Name') or (tag['Key'] == 'name'):                # Check for any tags with a value of Name or name
                name = tag['Value']               # Set name variable to be equal to the value of the Name/name tag
        print(region, " : ", name)                # Print the filtered instances formatted with the region followed by instance name
