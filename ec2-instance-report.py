from collections import defaultdict
import boto3
import os
import argparse

# Make the sript user-friendly by providing some arguments and help options
parser = argparse.ArgumentParser(description="Retrieve a list of AWS EC2 instances.")
parser.add_argument("-c", "--lifecycle", choices=['all', 'spot', 'scheduled'], type=str, help="All instances matching LIFECYCLE.")
parser.add_argument("-e", "--elastic-ip", type=str, help="All instances matching the ELASTIC_IP.")
parser.add_argument("-f", "--private-ip", type=str, help="All instances matching the PRIVATE_IP. ALWAYS DISPLAYED.")
parser.add_argument("-i", "--id", type=str, help="All instances matching ID, entered as a comma separated list. ALWAYS DISPLAYED.")
parser.add_argument("-l", "--launchtime", help="Display the instance launch time.", action="store_true")
parser.add_argument("-n", "--name", type=str, help="(Loose) All instances where 'Name' tag contains NAME, entered as a comma separated list.")
parser.add_argument("-N", "--name-exact", type=str, help="(Strict) All instances where 'Name' tag matches NAME exactly, entered as a comma separated list.")
parser.add_argument("-o", "--owner", type=str, help="(Loose) All instances where 'Owner' tag contains OWNER, entered as a comma separated list. ALWAYS DISPLAYED.")
parser.add_argument("-O", "--owner-exact", type=str, help="(Strict) All instances where 'Owner' tag matches OWNER exactly, entered as a comma separated list.")
parser.add_argument("-p", "--project", type=str, help="(Loose) All instances where 'Project' tag contains PROJECT, entered as a comma separated list. ALWAYS DISPLAYED.")
parser.add_argument("-P", "--project-exact", type=str, help="(Strict) All instances where 'Project' tag matches PROJECT exactly, entered as a comma separated list.")
parser.add_argument("-r", "--region", action='append', type=str, help="All instances in Region(s) REGION, multiple value allowed. ALWAYS DISPLAYED.")
parser.add_argument("-R", "--region-print", action='store_true', help="Print all available region names.")
state_args = ['pending', 'running', 'shutting-down', 'stopping', 'stopped', 'terminated']
parser.add_argument("-s", "--state", action='append', choices=state_args, help="All instances with Instance State STATE, multiple values allowed. ALWAYS DISPLAYED.")
parser.add_argument("-t", "--transition", help="", action="store_true")
parser.add_argument("--test", help="Debug, print all args", action="store_true")
args = parser.parse_args()

## CONFIRM THE CURRENT VALUES OF EACH ARGUMENT FOR TESTING
if args.test:
    print(args)
    print("\n")

if args.state:
    arg_state = args.state
else:
    arg_state = state_args

# Report should be run using restricted IAM Role.
# IAM 'ec2report' credentials should be stored as a boto3 profile (example: ~/.aws/credentials)
os.environ['AWS_PROFILE'] = 'ec2report'   # Define which profile to connect with
session = boto3.Session(profile_name='ec2report')   # Create a boto3 session using the defined profile

def get_region():
    global region_list
    # Obtain all publicly available regions
    region_list = session.get_available_regions('ec2')
    return region_list
    
def get_instances():
    # Declare dict to be used for storing instance details later
    ec2data = defaultdict()
    
    for region in arg_region:
        ec2 = boto3.resource('ec2', region)   # Print a delimiter to identify the current region
        instances = ec2.instances.filter(   # Filter the list of returned instances
            Filters=[
                {'Name': 'instance-state-name', 'Values': arg_state},    # Return only instances that are stopped or running
            ]
        )
        for instance in instances:
            # List of available attributes : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#instance
            tags = instance.tags
            name = "NO_NAME"
            owner = "NO_OWNER"
            project = "NO_PROJECT"
            if tags :
                for tag in tags:
                    key = tag['Key']
                    if str.lower(key) == 'name':    # Check for any tags with a value of Name or name
                        name = tag['Value']   # Set name variable to be equal to the value of the Name/name tag
                    if str.lower(key) == 'owner':
                        owner = tag['Value']
                    if str.lower(key) == 'project':
                        project = tag['Value']
    
            inst_id = instance.id
    
            if instance.state['Name']:
                state = instance.state['Name']
            else:
                state = 'NO_STATE'
    
            if instance.instance_lifecycle:
                lifecycle = instance.instance_lifecycle
            else:
                lifecycle = 'Scheduled'   # Boto 3 returns only 'spot'. Set to 'Scheduled' if not a spot instance
    
            if instance.private_ip_address:
                private_ip = instance.private_ip_address
            else:
                private_ip = 'NO_PRV_IP'
    
            if instance.public_ip_address:
                public_ip = instance.public_ip_address
            else:
                public_ip = 'NO_PUB_IP'
    
            inst_type = instance.instance_type
    
            if instance.launch_time:
                launch_time = instance.launch_time.strftime("%m/%d/%Y %H:%M:%S")
            else:
                launch_time = 'NO_LAUNCH'
    
            if instance.state_transition_reason:
                transition = instance.state_transition_reason
            else:
                transition = 'NO_TRANS'
    
            # Add instance info to a dictionary         
            ec2data[instance.id] = { 
                'Name': name,
                'Type': inst_type,
                'Lifecycle': lifecycle,
                'Owner' : owner,
                'State': state,
                'Private IP': private_ip,
                'Public IP': public_ip,
                'Launch Time': launch_time,
                'Transition Reason' : transition
                }
    
            # Print results line by line
            print(region + ' : ' + name + ', ' + inst_id + ', ' + inst_type + ', ' + lifecycle + ', ' + launch_time + ', ' + state + ', ' + transition + ', ' + private_ip + ', ' + public_ip + ', ' + owner + ', ' + project)

# Check if --region set and assign variable values
if args.region:
    arg_region = args.region
else:
    arg_region = get_region()

# Print print all available regions
if args.region_print:
    get_region()
    print('------------------')
    print('Available regions:')
    print('------------------')
    for region in region_list:
        print(region)
    print('------------------')
    print('Retrieved from AWS')
    print('------------------')

# Go ahead and output the instance details if not checking for a list of regions
if not args.region_print:
    get_instances()

'''
# Print results as a table
template = "{Name:10}|{Type:10}|{Lifecycle:10}"
print(template.format(Name="Name", Type="Type", Lifecycle="Lifecycle"))
attributes = ['Name', 'Type', 'Lifecycle', 'Owner', 'State', 'Private IP', 'Public IP', 'Launch Time']
for instance_id, instance in ec2data.items():
    for key in attributes:
        print(template.format(*key))
'''

'''
# Print results in blocks
attributes = ['Name', 'Type', 'Lifecycle', 'Owner', 'State', 'Private IP', 'Public IP', 'Launch Time']
for instance_id, instance in ec2data.items():
    for key in attributes:
        print("{0:10}|{1:10}".format(key, instance[key]))
    print("------")
'''
