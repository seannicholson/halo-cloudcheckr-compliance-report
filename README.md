# CloudCheckr / Halo Installation Compliance CSV Report


Disclaimer: This script is provided as is. USE AT YOUR OWN RISK.
NOT A SUPPORTED SOLUTION

# Configure
To configure script add API Key information to cloudpassage.yml File
CloudPassage API information
>key_id: your_api_key_id

>secret_key: your_api_secret_key

CloudChecker API information
>cloudchecker_api: your CloudCheckr API Key

# Requirements

This script requires Python 2.7.10 or greater
This script requires the CloudPassage Python SDK
> pip install cloudpassage

This script requires the Requests Python module.
>pip install requests

Install from pip with pip install cloudpassage. If you want to make modifications to the SDK you can install it in editable mode by downloading the source from this github repo, navigating to the top directory within the archive and running pip install -e . (note the . at the end). Or you can visit https://github.com/cloudpassage/cloudpassage-halo-python-sdk to clone it directly from our github.

# Running
Run *python cc_halo_complinace_report.py* to generate a CSV of Halo installations across your AWS
instances that are listed in CloudCheckr.
Will show based on AWS instance ID match if Halo is installed (requires Halo agent v3.9.5 or later)
Will show based on AWS AMI ID if the instance has a compatible OS. (If the AMI that the instance is based off is listed for a instance with Halo already installed, then Halo compatible will show as True)
Will check AMI descriptions for AMI's listed in OtherLinux category for OS string matches for Halo
compatible OSes.

# Reports
This script produces two CSV reports in the reports directly.
1. Halo Compliance Report with date stamp
2. List of all AMI current showing for active servers in the Halo portal with OS platform.


# Dependencies
Part of the script assumes you have labeled your servers with AWS account information to properly obtain the AWS Instance ID and AWS Account ID for Halo agent v3.8.3 and earlier. The script checks for this server label ("awsAccountID_awsInstanceID"), but only makes this check if the EC2 metadata is not present in the server details JSON.


# License

Copyright (c) 2017, CloudPassage, Inc. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met: * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer. * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution. * Neither the name of the CloudPassage, Inc. nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL CLOUDPASSAGE, INC. BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED ANDON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
