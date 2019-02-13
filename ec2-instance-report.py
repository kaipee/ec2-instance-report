from collections import defaultdict
import boto3
import os
import argparse

# Make the sript user-friendly by providing some arguments and help options
# Search filters
parser = argparse.ArgumentParser(description="Retrieve a list of AWS EC2 instances.")
parser.add_argument("-c", "--lifecycle", action="store_true", help="All instances matching LIFECYCLE.")
parser.add_argument("-e", "--elastic-ip", type=str, help="All instances matching the ELASTIC_IP.")
parser.add_argument("-f", "--private-ip", type=str, help="All instances matching the PRIVATE_IP. ALWAYS DISPLAYED.")
parser.add_argument("-i", "--id", type=str, help="All instances matching ID, entered as a comma separated list. ALWAYS DISPLAYED.")
#TODO : parser.add_argument("-nu", "--nameupper", type=str, help="(Loose) All instances where 'Name' tag contains NAME, accepts multiple values.")
parser.add_argument("-NL", "--name-exact-lower", type=str, help="(Strict) All instances where 'name' tag matches NAME exactly, accepts multiple values.")
parser.add_argument("-NU", "--name-exact-upper", type=str, help="(Strict) All instances where 'NAME' tag matches NAME exactly, accepts multiple values.")
parser.add_argument("-NS", "--name-exact-sentence", type=str, help="(Strict) All instances where 'Name' tag matches NAME exactly, accepts multiple values.")
parser.add_argument("-x", "--custom-tag", action='append', help="(Loose) All instances where tag is like CUSTOM_TAG, accepts multiple values.")
#TODO : parser.add_argument("-o", "--owner", type=str, help="(Loose) All instances where 'Owner' tag contains OWNER, entered as a comma separated list. ALWAYS DISPLAYED.")
parser.add_argument("-OL", "--owner-exact-lower", type=str, help="(Strict) All instances where 'owner' tag matches OWNER exactly, entered as a comma separated list.")
parser.add_argument("-OU", "--owner-exact-upper", type=str, help="(Strict) All instances where 'OWNER' tag matches OWNER exactly, entered as a comma separated list.")
parser.add_argument("-OS", "--owner-exact-sentence", type=str, help="(Strict) All instances where 'Owner' tag matches OWNER exactly, entered as a comma separated list.")
#TODO : parser.add_argument("-p", "--project", type=str, help="(Loose) All instances where 'Project' tag contains PROJECT, accpets multiple values. ALWAYS DISPLAYED.")
parser.add_argument("-PL", "--project-exact-lower", type=str, help="(Strict) All instances where 'project' tag matches PROJECT exactly, accepts multiple values.")
parser.add_argument("-PU", "--project-exact-upper", type=str, help="(Strict) All instances where 'PROJECT' tag matches PROJECT exactly, accepts multiple values.")
parser.add_argument("-PS", "--project-exact-sentence", type=str, help="(Strict) All instances where 'Project' tag matches PROJECT exactly, accepts multiple values.")
parser.add_argument("-r", "--region", action='append', type=str, help="All instances in Region(s) REGION, accepts multiple values. ALWAYS DISPLAYED.")
parser.add_argument("-R", "--region-print", action='store_true', help="Print all available region names.")
state_args = ['pending', 'running', 'shutting-down', 'stopping', 'stopped', 'terminated']
parser.add_argument("-s", "--state", action='append', choices=state_args, help="All instances with Instance State STATE, accepts multiple values. ALWAYS DISPLAYED.")
parser.add_argument("--test", help="Debug, print all args", action="store_true")
# Display options (value printed if argument passed)
parser.add_argument("-l", "--launchtime", help="Display the instance launch time.", action="store_true")
parser.add_argument("-t", "--transition", help="Display last state transition details if availale.", action="store_true")

global args
args = parser.parse_args()

# Report should be run using restricted IAM Role.
# IAM 'ec2report' credentials should be stored as a boto3 profile (example: ~/.aws/credentials)
os.environ['AWS_PROFILE'] = 'ec2report'   # Define which profile to connect with
session = boto3.Session(profile_name='ec2report')   # Create a boto3 session using the defined profile

def get_filters():
    filters = {}
    
    # Filter for lifecycle if provided
    if args.lifecycle:
        filter_lifecycle = {
        'Name': 'instance-lifecycle',
        'Values': ['spot']
        }
        filters["lifecycle"] = filter_lifecycle
    
    # Filter for Elastic IP if provided
    if args.elastic_ip:
        filter_elasticip = {
        'Name': 'network-interface.association.public-ip',
        'Values': [args.elastic_ip]
        }
        filters["elasticip"] = filter_elasticip
    
    # Filter for Private IP if provided
    if args.private_ip:
        filter_privateip = {
        'Name': 'network-interface.addresses.private-ip-address',
        'Values': [args.private_ip]
        }
        filters["privateip"] = filter_privateip
    
    # Filter for Instance ID if provided
    if args.id:
        filter_instanceid = {
        'Name': 'instance-id',
        'Values': [args.id]
        }
        filters["instance_id"] = filter_instanceid

    ###################################################################    
    # Quick and dirty - AWS API_FILTER is explicitly case-sensitive
    #                   and do not accept logic (no OR, explicitly AND).
    #                   Tag keys may be upper, lower, or other case.
    #                   Case-insensitive filter should be applied
    #                   programmatically after all results are returned
    ###################################################################
    # Filter for Tag : name
    if args.name_exact_lower:
        filter_name_e_l = {   # Search lowercase tag 'name'
        'Name': 'tag:name',
        'Values': [args.name_exact_lower]
        }
        filters["name"] = filter_name_e_l

    ###################################################################
    
    # Filter for custom tags if provided
    if args.custom_tag:
        filter_custag = {
        'Name': 'tag-key',
        'Values': args.custom_tag
        }
        filters["cust_tag"] = filter_custag
    
    # Filter for instance state (default to all)
    if args.state:
        arg_state = args.state    # Set the instance state depending on -s --state argument
    else:
        arg_state = state_args    # Set the instance state to a default list of all states
    filter_state = {
    'Name': 'instance-state-name',
    'Values': arg_state
    }
    filters["state"] = filter_state

    # Return filters
    for value in filters.values():
#        print(value) ##DEBUG
        return value

def get_region():
    global region_list
    # Obtain all publicly available regions
    region_list = session.get_available_regions('ec2')
    return region_list
    
def get_instances():
    # Declare dict to be used for storing instance details later
    ec2data = defaultdict()
    
    print("REGION\tNAME\tINSTANCE ID\tISNTANCE TYPE\tLIFECYCLE\tLAUNCH TIME\tSTATE\tLAST TRANSITION\tPRIVATE IP\tPUBLIC IP\tOWNER\tPROJECT")
    for region in arg_region:
        ec2 = boto3.resource('ec2', region)   # Print a delimiter to identify the current region
        instances = ec2.instances.filter(   # Filter the list of returned instance - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.PlacementGroup.filters
            # List of available filters : https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeInstances.html
            Filters=[
                get_filters()
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
    
                    if args.custom_tag:   # Loop over the list of custom tags if present
                        for custom_tag in args.custom_tag:
                            if tag['Key'] == custom_tag:
                                print(custom_tag + " : " + tag['Value'])
                                ctags[tag['Key']] = tag['Value']

            inst_id = instance.id
    
            if instance.state['Name']:
                state = instance.state['Name']
            else:
                state = 'NO_STATE'
    
            if instance.instance_lifecycle:
                lifecycle = instance.instance_lifecycle
            elif instance.instance_lifecycle is None:
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
            #for data in ec2data:
            #    print(data[3])
            print(region + "\t" + name + "\t" + inst_id + "\t" + inst_type + "\t" + lifecycle + "\t" + launch_time + "\t" + state + "\t" + transition + "\t" + private_ip + "\t" + public_ip + "\t" + owner + "\t" + project)

## CONFIRM THE CURRENT VALUES OF EACH ARGUMENT FOR TESTING
if args.test:
    print(args)
    print("\n")

# Check if --region set and assign variable values
if args.region:
    arg_region = args.region
else:
    arg_region = get_region()

# Print print all available regions if -R flag is set
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
else:
    # Go ahead and output the instance details if not checking for a list of regions
    ctags = {}
    get_instances()
#    print(get_filters()) ##DEBUG

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
