# ec2-instance-report

A Boto3 script to query EC2 and report any potentially abandoned instances

## Getting Started

### Prerequisites

This script requires the following packages.

* python
* boto3

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
