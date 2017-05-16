# WARNING: This script takes a long time to execute
# Author: Sean Nicholson
# Version 1.0.0
# Date 05.16.2017
##############################################################################

# Import Python Modules
import requests, json, csv, os
import cloudpassage
import yaml
import time
global api_session


# Define Methods
def create_api_session(session):
    config_file_loc = "cloudpassage.yml"
    config_info = cloudpassage.ApiKeyManager(config_file=config_file_loc)
    session = cloudpassage.HaloSession(config_info.key_id, config_info.secret_key)
    return session

def byteify(input):
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

def get_config():
    with open('cloudpassage.yml') as config_settings:
        api_info = yaml.load(config_settings)
        cc_key = ""
        cc_key = api_info['defaults']['cloudchecker_api']
    return cc_key


# Query CC API get_resources_ami_details endpoint to obtain list of all AMIs in
# OtherLinux that are running for ALL Intel Accounts.
# Get a list of all AMI's from Halo
# Perform text search match on AMI ID Description to check for compatible OS.
# Mark as compatible if AMI ID is listed in Halo or if AMI ID Description contains
# OS information and OS is supported by Halo.
def get_halo_compatible_ami_from_cc(session, cc_api_key):
    halo_servers_ami_list = get_halo_servers_ami_id(session)
    halo_compatible_ami=[]
    unique_ami_list = []
    ubuntu = ["ubuntu", "debian"]
    amiLinux = [ "amazon linux", "fedora", "rhel", "centos", "oracle", "redhat"]
    coreos = "coreos"
    halo_supported_amis = ['CentOs', 'RedHat', 'Windows', 'Ubuntu', 'Oracle', 'Debian', 'Amazon']
    cc_aws_accounts = requests.get("https://api.cloudcheckr.com/api/account.json/get_accounts_v2?access_key=" + str(cc_api_key))
    if cc_aws_accounts.status_code == 200:
        accounts_list_reply = cc_aws_accounts.json()
        account_list_json = accounts_list_reply['accounts_and_users']
        for account in account_list_json:
            if "EOL" not in account['account_name'] and account['aws_account_id']:
    #with open('aws_accountID.txt') as f:
    #    awsAccountIDs = f.readlines()
    #    for awsAccountID in awsAccountIDs:
            #print awsAccountID
                cloudcheckr_url = 'https://api.cloudcheckr.com/api/inventory.json/get_resources_ami_details?access_key=' + str(cc_api_key) + '&use_aws_account_id=' + str(account['aws_account_id'])
                cloudcheckr_url = cloudcheckr_url.strip()
                reply = requests.get(cloudcheckr_url)
                if reply.status_code == 200:
                    aws_instances = reply.json()
                    for instance in aws_instances['Amis']:
                        ami_halo_compatible = "Unknown"
                        ami_os_platform = "Unknown"
                        instance_str = byteify(instance)
                        if instance_str['ImageId'] not in unique_ami_list:
                            unique_ami_list.append(instance_str['ImageId'])
                            if instance_str['RunningInstanceCount'] > 0:
                                #print instance_str['ImageId']
                                description_clean = str(instance_str['Description']).replace(",","").lower()
                                description_clean = description_clean.strip()
                                if any (x in description_clean for x in ubuntu):
                                    ami_halo_compatible = "Maybe"
                                elif coreos in description_clean:
                                    ami_halo_compatible = "Unknown"
                                elif any (x in description_clean for x in amiLinux):
                                    ami_halo_compatible = "Maybe"
                                elif instance_str['Platform'] in halo_supported_amis:
                                    ami_halo_compatible = True
                                    #aws_AccountID_str = str(awsAccountID).strip()
                                    #if instance_str['ImageId'] in halo_servers_ami_list.values():
                                    #    ami_halo_compatible = "True"
                                    #halo_servers_ami_list_conversion = dict((i['ami_image_id'], i['os_platform']) for i in halo_servers_ami_list)
                                for item in halo_servers_ami_list:
                                    if instance_str['ImageId'] == item['ami_image_id']:
                                            #print instance_str['ImageId']
                                            #print item['os_platform']
                                        if 'coreos' not in item['os_platform']:
                                            ami_halo_compatible = "True"
                                        else:
                                            ami_halo_compatible = "Unknown"
                                        ami_os_platform = item['os_platform']
                                        break
                                    #if instance_str['ImageId'] not in unique_ami_list:
                                halo_compatible_ami.append({'cc_ami_id': instance_str['ImageId'], "description": description_clean, "halo_compatible": ami_halo_compatible, "halo_os_platform": ami_os_platform })


    #print halo_compatible_ami
    print "CC List of Halo compatible AMI's complete " + time.strftime("%Y%m%d-%H%M%S")
    return halo_compatible_ami, account_list_json



# Get CC API get_resources_ec2_details to obtain list of all Platform =
# OtherLinux and Status = Running for ALL Intel Accounts. Compare the Instances List for Halo status
# and AMI ID details. Write list of instances to CSV.

def get_cloudcheckr_ec2_instances(session, cc_api_key):
    halo_servers_instance_id_list = get_halo_servers_instance_id(session)
    halo_compatible_cc_ami, cc_aws_accounts_list = get_halo_compatible_ami_from_cc(session, cc_api_key)
    if not os.path.exists("reports"):
          os.makedirs("reports")
    out_file = "reports/CC_Halo_Compliance_Report_" + time.strftime("%Y%m%d-%H%M%S") + ".csv"
    ofile  = open(out_file, "w")
    ofile.write('AWS Account,Instance ID,AMI Image ID,Launch Date,Halo Installed,Halo Compatible, Halo OS Platform, CC OS Platform, AMI Description')
    #halo_servers_list=get_halo_servers_instance_id(session)
    #halo_ami_list=get_halo_servers_ami_id(session)
    halo_supported_oses = ['CentOs', 'RedHat', 'Windows', 'Ubuntu', 'Oracle', 'Debian', 'Amazon']
    for account in cc_aws_accounts_list:
        if "EOL" not in account['account_name'] and account['aws_account_id']:
    #with open('aws_accountID.txt') as f:
    #    awsAccountIDs = f.readlines()
    #    for awsAccountID in awsAccountIDs:
            print account['aws_account_id']
            cloudcheckr_url = 'https://api.cloudcheckr.com/api/inventory.json/get_resources_ec2_details?access_key=' + str(cc_api_key) + '&use_aws_account_id=' + str(account['aws_account_id'])
            cloudcheckr_url = cloudcheckr_url.strip()
            reply = requests.get(cloudcheckr_url)
            if reply.status_code == 200:
                aws_instances = reply.json()
                aws_instances = byteify(aws_instances)
                for instance in aws_instances['Ec2Instances']:
                    instance_launch = ""
                    halo_compatible = "Unknown"
                    instance_description = "Unknown"
                    halo_installed = False
                    halo_os_platform = "Unknown"
                    #print "InstanceId: %s" % instance['InstanceId']
                    if instance['Status'] == "running":
                        instance_launch = instance['LaunchTime'].split("T")
                        if instance['Platform'] in halo_supported_oses:
                            halo_compatible = True
                        for halo_instance_id in halo_servers_instance_id_list:
                            #print halo_instance_id['ami_instance_id']
                            if instance['InstanceId'].strip() == halo_instance_id['ami_instance_id'].strip():
                                halo_installed = True
                                #print "Halo Installed"
                                #print "Instance %s == Halo Instance %s" % instance['InstanceId'], halo_instance_id['ami_instance_id']
                                halo_os_platform = halo_instance_id['platform']
                                if "coreos" not in halo_instance_id['platform']:
                                    halo_compatible = True
                                break
                        #print instance['AMI']
                        for cc_ami in halo_compatible_cc_ami:
                            #print cc_ami['cc_ami_id']
                            if instance['AMI'] == cc_ami['cc_ami_id']:
                                #print "AMI ID match in halo_compatible_cc_ami"
                                instance_description = cc_ami['description']
                                halo_os_platform = cc_ami['halo_os_platform']
                                if "coreos" in halo_os_platform:
                                    halo_compatible = False
                                if halo_installed == True and "coreos" not in halo_os_platform:
                                    halo_compatible = True
                                else:
                                    halo_compatible = cc_ami['halo_compatible']
                                break
                        aws_AccountID_str = str(account['aws_account_id']).strip()
                        ofile.write('\n')
                        row = "'{0}',{1},{2},{3},{4},{5},{6},{7},{8}".format(aws_AccountID_str, instance['InstanceId'], instance['AMI'],instance_launch[0], halo_installed, halo_compatible, halo_os_platform, instance['Platform'], instance_description)
                        ofile.write(row)
                        #print row
    ofile.close()
    print "CC Instance and AMI compare with Halo CSV creation complete " + time.strftime("%Y%m%d-%H%M%S")







# Query Halo API /v1/servers to get list of AMI IDs with Halo Installed.
def get_halo_servers_ami_id(session):
    get_halo_servers_list = cloudpassage.HttpHelper(session)
    reply=get_halo_servers_list.get_paginated("/v1/servers?state=active","servers",20)
    halo_ami_list=[]
    unique_ami = []
    if not os.path.exists("reports"):
        os.makedirs("reports")
    out_file = "reports/halo_ami_list_" + time.strftime("%Y%m%d-%H%M%S") + ".csv"
    oamifile  = open(out_file, "w")
    oamifile.write('AMI Image ID,OS PLatform')
    for server in reply:
        if 'aws_ec2' in server:
            ec2_data = server['aws_ec2']
            if ec2_data['ec2_image_id'] not in unique_ami:
                halo_ami_list.append({'ami_image_id':ec2_data['ec2_image_id'],'os_platform': server['platform']})
                unique_ami.append(ec2_data['ec2_image_id'])
                oamifile.write('\n')
                rowami = "{0},{1}".format(ec2_data['ec2_image_id'],server['platform'])
                oamifile.write(rowami)
    oamifile.close()
    halo_ami_list = byteify(halo_ami_list)
    #print halo_ami_list
    print "Halo AMI List Complete " + time.strftime("%Y%m%d-%H%M%S")
    return halo_ami_list

# Query Halo API /v1/servers to get list of servers and extract Instance ID
def get_halo_servers_instance_id(session):
    old_agent_count = 0
    get_halo_servers_list = cloudpassage.HttpHelper(session)
    reply=get_halo_servers_list.get_paginated("/v1/servers?state=active","servers",10)
    halo_instance_id_list=[]
    for server in reply:
        if 'aws_ec2' in server:
            ec2_data = server['aws_ec2']
            halo_instance_id_list.append({'ami_instance_id':ec2_data['ec2_instance_id'], 'platform': server['platform'], 'ami_image_id': ec2_data['ec2_image_id']})
        elif server['server_label'] and "_" in server['server_label']:
            server_label = server['server_label']
            server_label_parts = server_label.split("_")
            #print server_label_parts[1]
            #old_agent_count += 1
            server_label_instance = server_label_parts[1]
            halo_instance_id_list.append({'ami_instance_id':server_label_instance,'platform': server['platform'],'ami_image_id':""})
    halo_instance_id_list = byteify(halo_instance_id_list)
    print "Halo AWS Instance ID Lookup Complete " + time.strftime("%Y%m%d-%H%M%S")
    return halo_instance_id_list




if __name__ == "__main__":
    api_session = None
    api_session = create_api_session(api_session)
    get_cloudcheckr_ec2_instances(api_session, get_config())
