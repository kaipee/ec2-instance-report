# ec2-instance-report

A Boto3 script to query EC2 and report any potentially abandoned instances

## Getting Started

### Prerequisites

This script requires the following packages.

* [python 3](https://www.python.org/downloads/)
* [boto3](https://github.com/boto/boto3)

This script uses access keys from IAM role 'ec2report'. The keys are expected to be located in `~/.aws/credentials`.

1. Login to AWS and obtain the AWS_ACCESS_KEY and AWS_SECRET_ACCESS_KEY form IAM role `ec2report`.
2. Create the boto3 credentials file `~/.aws/credentials` if it does not already exist.
3. Save the **ec2report** IAM role credentials in the following format.

```
[ec2report]
aws_access_key_id=[AWS_KEY]
aws_secret_access_key=[AWS_SECRET]
```

4. Secure the permission of the `~/.aws/credentials` file.

```
sudo chmod 600 ~/.aws/credentials
```


# TODO

Take arguments in the following format (all arguments are cumulative)

## Search Filters
| Flag | Argument | Description | Defaults |
| :--- | :--- | :--- | :--- |
| **-r** | **--region {filter}** | Take one or more regions as search filter | List all regions |
| **-s** | **--state {filter}** | Take one or more __expected values__<br><br>* pending<br>* running<br>* shutting-down<br>* terminated<br>* stopping<br>* stopped | Display all instances regardless of state |
| **-t** | **--type {filter}** | Take one or more instance types as search filter | List all types |
| **-i** | **--id {filter}** | Take one or more instance ids as search filter | List all instance ids |
| **-n** | **--name {filter}** | Take one ore more Name tags as a search filter (contains) | List all instance Name tags |
| **-N** | **--name-exact {filter}** | Take one ore more Name tags as a search filter (exact) | List all instance Name tags |
| **-o** | **--owner {filter}** | Take one ore more Owner tags as a search filter (contains) | List all instance Owner tags |
| **-O** | **--owner-exact {filter}** | Take one ore more Owner tags as a search filter (exact) | List all instance Owner tags |
| **-p** | **--project {filter}** | Take one ore more Project tags as a search filter (contains) | List all instance Project tags |
| **-P** | **--project-exact {filter}** | Take one ore more Project tags as a search filter (exact) | List all instance Project tags |
| **-e** | **--public {filter}** | Filter results matching exactly the elastic IP (Public IP) | List all instances with or without EIP |
| **-f** | **--private {filter}** | Filter results matching exactly the Private IP | List all instances with or without Private IP |

## Display Options
| Flag | Argument | Description | Defaults |
| :--- | :--- | :--- | :--- |
| **-l** | **--lifecycle** | Display instance lifecycle type (spot or scheduled) | Do not display |
| **-t** | **--transition** | Display last transition state details if present | Do not display |

~~Use a restricted IAM role - do not use individual credentials!!~~

~~Report from all regions by default~~
~~* return a list of all regions~~
~~* loop over each available region and report ec2 instances within~~

Provide multi/single-region options
* Print available choices and take user input
* assign user input to variable
* loop over array of choices and report on each chosen region

Group by Region then instance state (sort by State Transition Date old>new)

Print to stdout in JSON or Table format

Provide a total per region

Export to CSV report : reports/{MONTH_YEAR}/{datestamp}_{REGIONS}.csv
