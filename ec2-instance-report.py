from pprint import pprint as pp
import boto3
import os
import argparse

# Define output color classes
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# AWS example code ref : https://github.com/awsdocs/aws-doc-sdk-examples/tree/master/python/example_code

# Report should be run using restricted IAM Role.
# IAM 'ec2report' credentials should be stored as a boto3 profile (example: ~/.aws/credentials)
os.environ['AWS_PROFILE'] = 'script_ec2instancereport'   # Define which profile to connect with
session = boto3.Session(profile_name='script_ec2instancereport')   # Create a boto3 session using the defined profile

######################
# Set up the arguments
######################

# Make the sript user-friendly by providing some arguments and help options
# Search filters
parser = argparse.ArgumentParser(description="Retrieve a list of AWS EC2 instances.")

g_filters = parser.add_argument_group('SEARCH FILTERS')
g_display = parser.add_argument_group('DISPLAY OPTIONS')
g_debug = parser.add_argument_group('DEBUG')

# Search filters
g_filters.add_argument("-c", "--lifecycle", action="store_true", help="Only spot instances.")
g_filters.add_argument("-e", "--elastic-ip", type=str, help="Only instances matching the ELASTIC_IP.")
g_filters.add_argument("-f", "--private-ip", type=str, help="Only instances matching the PRIVATE_IP. ALWAYS DISPLAYED.")
g_filters.add_argument("-i", "--id", action='append', help="Only instances matching ID, accepts multiple values. ALWAYS DISPLAYED.")
#TODO : parser.add_argument("-nu", "--nameupper", type=str, help="(Loose) All instances where 'Name' tag contains NAME, accepts multiple values.")
g_filters.add_argument("-NL", "--name-exact-lower", action='append', help="(Strict) Only instances where 'name' tag matches NAME exactly, accepts multiple values.")
g_filters.add_argument("-NU", "--name-exact-upper", action='append', help="(Strict) Only instances where 'NAME' tag matches NAME exactly, accepts multiple values.")
g_filters.add_argument("-NS", "--name-exact-sentence", action='append', help="(Strict) Only instances where 'Name' tag matches NAME exactly, accepts multiple values.")
#TODO : parser.add_argument("-o", "--owner", type=str, help="(Loose) All instances where 'Owner' tag contains OWNER, entered as a comma separated list. ALWAYS DISPLAYED.")
g_filters.add_argument("-OL", "--owner-exact-lower", action='append', help="(Strict) Only instances where 'owner' tag matches OWNER exactly, accepts multiple values.")
g_filters.add_argument("-OU", "--owner-exact-upper", action='append', help="(Strict) Only instances where 'OWNER' tag matches OWNER exactly, accepts multiple values.")
g_filters.add_argument("-OS", "--owner-exact-sentence", action='append', help="(Strict) Only instances where 'Owner' tag matches OWNER exactly, accepts multiple values.")
#TODO : parser.add_argument("-p", "--project", type=str, help="(Loose) All instances where 'Project' tag contains PROJECT, accpets multiple values. ALWAYS DISPLAYED.")
g_filters.add_argument("-PL", "--project-exact-lower", action='append', help="(Strict) Only instances where 'project' tag matches PROJECT exactly, accepts multiple values.")
g_filters.add_argument("-PU", "--project-exact-upper", action='append', help="(Strict) Only instances where 'PROJECT' tag matches PROJECT exactly, accepts multiple values.")
g_filters.add_argument("-PS", "--project-exact-sentence", action='append', help="(Strict) Only instances where 'Project' tag matches PROJECT exactly, accepts multiple values.")
g_filters.add_argument("-r", "--region", action='append', type=str, help="Only instances in Region(s) REGION, accepts multiple values. ALWAYS DISPLAYED.")
state_args = ['pending', 'running', 'shutting-down', 'stopping', 'stopped', 'terminated']
g_filters.add_argument("-s", "--state", action='append', choices=state_args, help="Only instances with Instance State STATE, accepts multiple values. ALWAYS DISPLAYED.")
g_filters.add_argument("-x", "--custom-tag", action='append', help="(Loose) Only instances where tag is like CUSTOM_TAG, accepts multiple values.")

# Display options (value printed if argument passed)
g_display.add_argument("--colour", help="Colorize the output.", action="store_true")
g_display.add_argument("-l", "--launchtime", help="Display the instance launch time.", action="store_true")
g_display.add_argument("-t", "--transition", help="Display last state transition details if availale.", action="store_true")

# Debug filters
g_debug.add_argument("--debug-args", help="Debug, print all args", action="store_true")
g_debug.add_argument("--debug-filters", help="Debug, print all filters", action="store_true")
g_debug.add_argument("--debug-dict", help="Debug, print the ec2data dictionary", action="store_true")
g_debug.add_argument("-R", "--region-print", action='store_true', help="Print all publicly available region names.")
g_debug.add_argument("-Z", "--zone-print", action='store_true', help="Print all availablity zones and status.")

global args
args = parser.parse_args()

##############################
# Define the various functions
##############################

def get_filters(): # Filter instance results by AWS API_Filter attributes that are not Tags and do not require fuzzy searching (tag filtering should be case-insensitive)
    global filters
    filters = {}
    
    # Filter for lifecycle if provided
    if args.lifecycle:
        filters["lifecycle"] = {
            'Name': 'instance-lifecycle',
            'Values': ['spot']
        }
    
    # Filter for Elastic IP if provided
    if args.elastic_ip:
        filters["elasticip"] = {
            'Name': 'network-interface.association.public-ip',
            'Values': [args.elastic_ip]
        }
    
    # Filter for Private IP if provided
    if args.private_ip:
        filters["privateip"] = {
            'Name': 'network-interface.addresses.private-ip-address',
            'Values': [args.private_ip]
        }
    
    # Filter for Instance ID if provided
    if args.id:
        filters["instance_id"] = {
            'Name': 'instance-id',
            'Values': args.id
        }

    ###################################################################    
    # Quick and dirty - AWS API_FILTER is explicitly case-sensitive
    #                   and do not accept logic (no OR, explicitly AND).
    #                   Tag keys may be upper, lower, or other case.
    #                   Case-insensitive filter should be applied
    #                   programmatically after all results are returned
    ###################################################################
    # Tag : name|NAME|Name
    ###################################################################
    # Filter for Tag : name
    if args.name_exact_lower:
        filters["name_exact_low"] = {
            'Name': 'tag:name',
            'Values': args.name_exact_lower
        }

    # Filter for Tag : NAME
    if args.name_exact_upper:
        filters["name_exact_upp"]= {
            'Name': 'tag:NAME',
            'Values': args.name_exact_upper
        }

    # Filter for Tag : Name
    if args.name_exact_sentence:
        filters["name_exact_sent"] = {
            'Name': 'tag:Name',
            'Values': args.name_exact_sentence
        }

    ###################################################################
    # Tag : owner|OWNER|Owner
    ###################################################################
    # Filter for Tag : owner 
    if args.owner_exact_lower:
        filters["owner_exact_low"] = {
            'Name': 'tag:owner',
            'Values': args.owner_exact_lower
        }

    # Filter for Tag : OWNER
    if args.owner_exact_upper:
        filters["owner_exact_upp"]= {
            'Name': 'tag:OWNER',
            'Values': args.owner_exact_upper
        }

    # Filter for Tag : Owner
    if args.owner_exact_sentence:
        filters["owner_exact_sent"] = {
            'Name': 'tag:Owner',
            'Values': args.owner_exact_sentence
        }

    ###################################################################
    # Tag : project|PROJECT|Project
    ###################################################################
    # Filter for Tag : project 
    if args.project_exact_lower:
        filters["project_exact_low"] = {
            'Name': 'tag:project',
            'Values': args.project_exact_lower
        }

    # Filter for Tag : PROJECT
    if args.project_exact_upper:
        filters["project_exact_upp"] = {
            'Name': 'tag:PROJECT',
            'Values': args.project_exact_upper
        }

    # Filter for Tag : Project
    if args.project_exact_sentence:
        filters["project_exact_sent"] = {
            'Name': 'tag:Project',
            'Values': args.project_exact_sentence
        }

    ###################################################################
    
    # Filter for instance state (default to all)
    if args.state:
        arg_state = args.state    # Set the instance state depending on -s --state argument
    else:
        arg_state = state_args    # Set the instance state to a default list of all states
    filters["state"]= {
        'Name': 'instance-state-name',
        'Values': arg_state
    }

    # Filter for custom tags if provided
    if args.custom_tag:
        filters["cust_tag"] = {
            'Name': 'tag-key',
            'Values': args.custom_tag
        }
    
    if not args.debug_filters:
        # Return filters
        Filters = []
        for value in filters.values():
            Filters.append(value)
        return Filters

def get_region():
    global region_list
    # Obtain all publicly accessible regions for this session
    region_list = session.get_available_regions('ec2')
    return region_list
    
def get_zone():
    global zone_list
    print('--------------------')
    for region in arg_region:
       print('REGION : ' + region)
       print('--------------------')
       client = boto3.client('ec2', region)
       # Obtain all accessible availablility zones for this session
       zone_list = client.describe_availability_zones()['AvailabilityZones']
       for zone in zone_list:
           if zone['State'] == 'available':
               if args.colour:
                   print(zone['ZoneName'] + " : " + bcolors.OKGREEN + zone['State'] + bcolors.ENDC)
               else:
                   print(zone['ZoneName'] + " : " + zone['State'])
           else:
               if args.color:
                   print(zone['ZoneName'] + " : " + bcolors.FAIL + zone['State'] + bcolors.ENDC)
               else:
                   print(zone['ZoneName'] + " : " + zone['State'])
       print('--------------------')
    
def get_instances():
    global ec2data
    ec2data = dict()   # Declare dict to be used for storing instance details later
    ctags = dict()    # Declare dict to store all custom tag key:value pairs
    
    if not args.debug_dict:
        print("REGION\tNAME\tOWNER\tPROJECT\tINSTANCE ID\tINSTANCE TYPE\tLIFECYCLE\tLAUNCH TIME\tSTATE\tLAST TRANSITION\tPRIVATE IP\tPUBLIC IP")

    for region in arg_region:
        ec2 = boto3.resource('ec2', str.lower(region))   # Print a delimiter to identify the current region
        instances = ec2.instances.filter(   # Filter the list of returned instance - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.ServiceResource.instances 
            # List of available filters : https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeInstances.html
            Filters=get_filters()
        )
        for instance in instances:
            # List of available attributes : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#instance
            # Retrieve all instance attributes and assign desired attributes to dict that can be iterated over later
            if args.colour:
                ec2data[instance.id] = {
                    'Region': str.lower(region),
                    'Name': bcolors.WARNING + "NO_NAME" + bcolors.ENDC,
                    'Owner': bcolors.WARNING + "NO_OWNER" + bcolors.ENDC,
                    'Project': bcolors.WARNING + "NO_PROJECT" + bcolors.ENDC,
                    'Instance ID': instance.id,
                    'Type': bcolors.WARNING + "UNKNOWN_TYPE" + bcolors.ENDC,
                    'Lifecycle': 'Scheduled',   # Boto 3 returns only 'spot'. Set to 'Scheduled' if not a spot instance
                    'Launch Time': bcolors.WARNING + 'NO_LAUNCH' + bcolors.ENDC,
                    'State': bcolors.WARNING + "STATE_UND" + bcolors.ENDC,
                    'Transition Reason': bcolors.WARNING + 'NO_TRANS' + bcolors.ENDC,
                    'Private IP': bcolors.WARNING + 'NO_PRV_IP' + bcolors.ENDC,
                    'Public IP': 'NO_PUB_IP'
                    }
            else:
                ec2data[instance.id] = {
                    'Region': str.lower(region),
                    'Name': "NO_NAME",
                    'Owner': "NO_OWNER",
                    'Project': "NO_PROJECT",
                    'Instance ID': instance.id,
                    'Type': "UNKNOWN_TYPE",
                    'Lifecycle': 'Scheduled',   # Boto 3 returns only 'spot'. Set to 'Scheduled' if not a spot instance
                    'Launch Time': 'NO_LAUNCH',
                    'State': "STATE_UND",
                    'Transition Reason': 'NO_TRANS',
                    'Private IP': 'NO_PRV_IP',
                    'Public IP': 'NO_PUB_IP'
                    }
            tags = instance.tags
            if tags :
                for tag in tags:
                    key = tag['Key']
                    if str.lower(key) == 'name':    # Check for any tags with a value of Name or name
                        name = tag['Value']   # Set name variable to be equal to the value of the Name/name tag
                        ec2data[instance.id].update({'Name': name})
                    if str.lower(key) == 'owner':
                        owner = tag['Value']
                        ec2data[instance.id].update({'Owner' : owner})
                    if str.lower(key) == 'project':
                        project = tag['Value']
                        ec2data[instance.id].update({'Project' : project})
    
                    if args.custom_tag:   # Loop over the list of custom tags if present
                        for custom_tag in args.custom_tag:
                            if tag['Key'] == custom_tag:
                                ctags[tag['Key']] = tag['Value']
                                ec2data[instance.id].update(ctags)

            # Update instance info in dict
            if instance.launch_time:
                ec2data[instance.id].update({'Launch Time': instance.launch_time.strftime("%m/%d/%Y %H:%M:%S")})
    
            if instance.instance_lifecycle:
                ec2data[instance.id].update({'Lifecycle': instance.instance_lifecycle})
    
            if instance.public_ip_address:
                ec2data[instance.id].update({'Public IP': instance.public_ip_address})
    
            if instance.private_ip_address:
                ec2data[instance.id].update({'Private IP': instance.private_ip_address})
    
            if instance.state['Name']:
                if instance.state['Name'] == 'terminated':
                    if args.colour:
                        ec2data[instance.id].update({'State': bcolors.FAIL + instance.state['Name'] + bcolors.ENDC})    # Highlight terminated instances
                    else:
                        ec2data[instance.id].update({'State': instance.state['Name']})    # Highlight terminated instances
                elif instance.state['Name'] == 'stopped':
                    if args.colour:
                        ec2data[instance.id].update({'State': bcolors.WARNING + instance.state['Name'] + bcolors.ENDC})   # Highlight stopped instances
                    else:
                        ec2data[instance.id].update({'State': instance.state['Name']})   # Highlight stopped instances
                else:
                    ec2data[instance.id].update({'State': instance.state['Name']})
    
            if instance.state_transition_reason:
                ec2data[instance.id].update({'Transition Reason' : instance.state_transition_reason})
    
            if instance.instance_type:
                ec2data[instance.id].update({'Type' : instance.instance_type})
    
            # Print results line by line
            if not args.debug_dict:
                data = ec2data[instance.id]
                print("\t".join(ec2data[instance.id].values()))

##############
# Do the stuff
##############
instance_print = True

## CONFIRM THE CURRENT VALUES OF EACH ARGUMENT FOR TESTING
if args.debug_args:
    pp(args)
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
    instance_print = False

if args.debug_filters:
    get_filters()
    # Print the list of filters and values
    if args.region:
        print('-----------------')
        print('FILTERED REGIONS')
        print('-----------------')
        for region in arg_region:
            print(str.lower(region))
        print("\n")
    instance_print = False
    print("-----------")
    print("FILTER LIST")
    print("-----------")
    print(filters)    # Print the full currently assigned filters dict

    print("\n-------------")
    print("FILTER KEYS")
    print("-------------")
    for value in filters.keys():    # Print each currently defined filter key
        print(value)

    print("\n-------------")
    print("FILTER VALUES")
    print("-------------")
    for value in filters.values():    # Print each currently defined filter value
        pp(value)

if args.debug_dict:
    get_instances()
    print("------------------")
    print("EC2DATA DICTIONARY")
    print("------------------")
    pp(ec2data)
    for i_id, i_v in ec2data.items():
        print("-------------------")
        print(i_id)
        print("-------------------")
        for title, attribute in i_v.items():
            print(title, attribute, sep=" : ")

if args.zone_print:
    get_zone()
    instance_print = False

if instance_print:
    # Go ahead and output the instance details if not checking for a list of regions
    get_instances()
