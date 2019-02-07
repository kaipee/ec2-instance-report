import boto3
import os

# Report should be run using restricted IAM Role.
# IAM 'ec2report' credentials should be stored as a boto3 profile (example: ~/.aws/credentials)
os.environ['AWS_PROFILE'] = "ec2report"

# Define the AWS region
region_list = ['us-east-1']

for region in region_list:
    print ('REGION:', region)
    ec2 = boto3.resource('ec2', region)
    for instance in ec2.instances.all():#filter(Filters=[{'Name': 'instance-state-name', 'Values':['stopped', 'terminated']}]):
        mystate = instance.state['Name']
        if mystate ==  "stopped":
            print ('  instance:', instance, instance.tags)
