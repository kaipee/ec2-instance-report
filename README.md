# ec2-instance-report

A Boto3 script to query EC2 and report on instances with support for filtering Instance Tags and various attributes.

## Getting Started

### Prerequisites

#### Packages

This script requires the following packages.

* [python 3](https://www.python.org/downloads/)
* [boto3](https://github.com/boto/boto3)

#### Access Key

This script uses access keys from IAM profile 'script_ec2instancereport' by default. The keys are expected to be located in `~/.aws/credentials`.

1. Obtain the AWS_ACCESS_KEY and AWS_SECRET_ACCESS_KEY for IAM profile `script_ec2instancereport`. *(credentials can be obtained from DevOps team)*
2. Create the boto3 credentials file `~/.aws/credentials` if it does not already exist.
3. Save the **script_ec2instancereport** IAM account credentials in the following format.

```bash
[script_ec2instancereport]
aws_access_key_id=[AWS_KEY]
aws_secret_access_key=[AWS_SECRET]
```

4. Secure the permission of the `~/.aws/credentials` file.

```bash
sudo chmod 400 ~/.aws/credentials
```



## Usage

Simply executing the script will return a full, unfiltered, list of **all EC2 Instances** in **all regions** (that you have access to), grouped by region.

```bash
python ec2-instance-report.py
```

### Note

If you see the following error, please confirm you have access to all regions or pass each region that you do have access to as an argument `-r` (multiple regions accepted).

```bash
botocore.exceptions.ClientError: An error occurred (AuthFailure) when calling the DescribeInstances operation: AWS was not able to validate the provided access credentials
```

### Example output without arguments

```bash
REGION	NAME	OWNER	PROJECT	INSTANCE ID	INSTANCE TYPE	LIFECYCLE	LAUNCH TIME	STATE	LAST TRANSITION	PRIVATE IP	PUBLIC IP
us-east-1	instance1	auser	team-1	i-123456789abcdef	c4.xlarge	Scheduled	10/27/2017 14:59:48	stopped	User initiated (2017-10-31 09:30:13 GMT)	172.0.0.1	NO_PUB_IP
us-east-1	instance2	auser2	NO_PROJECT	i-123456987abcde	t2.large	Scheduled	07/18/2018 13:57:03	terminated	User initiated (2018-07-18 13:58:55 GMT)	172.0.0.2	NO_PUB_IP
ap-southeast-2	instance5	NO_OWNER	NO_PROJECT	i-123987456dbef	t2.micro	Scheduled	10/02/2017 19:03:12	running	NO_TRANS	172.0.0.5	52.60.4.200
```

Command-line arguments are available to filter the list of instances or hide/display columns.



## Command-line Arguments

### Search Filters
| Short | Long | Type | Description | Filter Case Sensitivity | Multiple Allowed |
| :--- | :--- | :--- | :--- | :--- | :--- |
| -p | --profile | String | Custom AWS profile | N/A | N/A |
| -c | --lifecycle | Boolean | Return only spot instances | N/A | N/A |
| -e | --elastic-ip {filter} | String | Return only instances associated with the elastic IP *{filter}* | N/A | No |
| -f | --private-ip {filter} | String | Return only instances associated with the Private IP *{filter}* | N/A | No |
| -i | --id {filter} | String | Return only instances that have Instance ID *{filter}* | Sensitive | Yes |
| -NL | --name-exact-lower {filter} | String | Return only instances that have Tag:**name** *{filter}* | Sensitive | Yes |
| -NU | --name-exact-upper {filter} | String | Return only instances that have Tag:**NAME** *{filter}* | Sensitive | Yes |
| -NS | --name-exact-sentence {filter} | String | Return only instances that have Tag:**Name** *{filter}* | Sensitive | Yes |
| -OL | --owner-exact-lower {filter} | String | Return only instances that have Tag:**owner** *{filter}* | Sensitive | Yes |
| -OU | --owner-exact-upper {filter} | String | Return only instances that have Tag:**OWNER** *{filter}* | Sensitive | Yes |
| -OS | --owner-exact-sentence {filter} | String | Return only instances that have Tag:**Owner** *{filter}* | Sensitive | Yes |
| -PL | --project-exact-lower {filter} | String | Return only instances that have Tag:**project** *{filter}* | Sensitive | Yes |
| -PU | --project-exact-upper {filter} | String | Return only instances that have Tag:**PROJECT** *{filter}* | Sensitive | Yes |
| -PS | --project-exact-sentence {filter} | String | Return only instances that have Tag:**Project** *{filter}* | Sensitive | Yes |
| -r | --region {filter} | String | Return only instances in the region *{filter}* | Insensitive | Yes |
| -s | --state {filter} | Expected String | Return only instances with state : <br><br>* pending<br>* running<br>* shutting-down<br>* terminated<br>* stopping<br>* stopped | Sensitive | Yes |
| -x | --custom-tag {filter} | String | Return only instances with Tag:*{filter}* | Sensitive | Yes |

### Display Options
| Short | Long | Type | Description |
| :--- | :--- | :--- | :--- |
| | **--colour** | Boolean | Display coloured output (highlights missing tags and instance states) |
| -l | --launchtime | Boolean | Display instance Launch Time |
| -t | --transition | Boolean | Display last transition state details (if present, otherwise show NO_TRANS) |

### Debug Options
| Short | Long | Type | Description |
| :--- | :--- | :--- | :--- |
| | --debug-args | Boolean | Print all currently passed arguments |
| | --debug-filters | Boolean | Print all currently passed search filters |
| | --debug-dict | Boolean | Pretty print the ec2data dictionary |
| -R | --region-print | Boolean | Retrieve a list of all currently available AWS Regions |
| -Z | --zone-print | Boolean | Retrieve a list of all currently available AWS Availability Zones, grouped by Region, and display status |


## Examples

Find ALL RUNNING instances in US-EAST-1 with no name AND no owner AND no project. Exported to tab-delimited CSV file.

```
python ec2-instance-report.py -r us-east-1 -s running | grep -E 'NO_NAME.*NO_OWNER.*NO_PROJECT' > ~/tmp/ec2_running-missing-all_$(date +%F_%T).csv
```

Find ALL RUNNING instances in US-EAST-1 with EITHER no name OR no owner OR no project. Exported to tab-delimited CSV file.

```
python ec2-instance-report.py -r us-east-1 -s running | grep 'NO_OWNER\|NO_PROJECT\|NO_NAME' > ~/tmp/ec2_running-missing-1_$(date +%F_%T).csv
```

Find ALL stopped instances in US-EAST-1. Exported to tab-delimited CSV file.

```
python ec2-instance-report.py -r us-east-1 -s stopped -s stopping -s shutting-down > ~/tmp/ec2_stopped_$(date +%F_%T).csv
```


## TODO

## Error handling
* Notify and move on if Session does not have access to a specific region.

### Case sensitivity
Implement case-insensitive filter for the following:
* Name
* Name-exact
* Owner
* Owner-exact
* Project
* Project-exact
* Custom
* Custom-exact

### Default column display
Display only the following attributes by default, display others when arguments provided
* Region
* ID
* State
* Name
* Owner
* Project
* Private IP

### Group and sort
Group by Region then sort by transition date old>new

### Format display
* Print to stdout in Table format
* Provide a total per region

### Export data
Export to CSV report : reports/{MONTH_YEAR}/{datestamp}_{REGIONS}.csv

# License

Licensed under GNU General Public License v3.0
