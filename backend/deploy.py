import os
import boto3
import subprocess
import sys
import time
import dotenv

dotenv.load_dotenv()
client = boto3.client("ec2", region_name=os.getenv("REGION_NAME"))

def create_and_save_key_pair(name):
    key_pair = client.create_key_pair(KeyName=name)
    key_name = key_pair["KeyName"]
    with open(f"{key_name}.pem", "w") as file:
        file.write(key_pair["KeyMaterial"])

    subprocess.run(["chmod", "400", f"{key_name}.pem"])

def create_security_group(name):
    security_group = client.create_security_group(
        GroupName=name,
        Description=f"ECE326 Security Group named {name}"
    )
    group_id = security_group["GroupId"]

    client.authorize_security_group_ingress(
        GroupId=group_id,
        IpPermissions=[
            {"IpProtocol": "ICMP", "FromPort": -1, "ToPort": -1, "IpRanges": [{"CidrIp":"0.0.0.0/0"}]},
            {"IpProtocol": "TCP", "FromPort": 22, "ToPort": 22, "IpRanges": [{"CidrIp":"0.0.0.0/0"}]},
            {"IpProtocol": "TCP", "FromPort": 80, "ToPort": 80, "IpRanges": [{"CidrIp":"0.0.0.0/0"}]},
            {"IpProtocol": "TCP", "FromPort": 8000, "ToPort": 8000, "IpRanges": [{"CidrIp":"0.0.0.0/0"}]}
        ]
    )

startup_script = """#!/bin/bash
echo "Inside startup script" >> startup-log.txt
cd /home/ubuntu
echo "Changed to ubuntu" >> startup-log.txt
sudo apt update -y
echo "Updated apt" >> startup-log.txt
sudo apt install -y python3-pip
echo "Installed pip" >> startup-log.txt
sudo apt install -y python3.12-venv
echo "Installed venv" >> startup-log.txt
python3 -m venv venv
echo "Created venv" >> startup-log.txt
sudo chmod -R a+rwx venv
echo "Updated permissions" >> startup-log.txt
source venv/bin/activate
echo "Activated venv" >> startup-log.txt
pip3 install fastapi uvicorn langchain faiss-cpu beautifulsoup4 python-multipart rank_bm25 langchain-core nltk pdfplumber cohere python-dotenv psutil spacy
echo "Installed packages" >> startup-log.txt
"""

def create_and_run_instance(key_pair_name, security_group_name):
    instance = client.run_instances(
        ImageId="ami-04b4f1a9cf54c11d0",
        InstanceType="t2.medium",
        KeyName=key_pair_name,
        SecurityGroups=[security_group_name],
        MinCount=1,
        MaxCount=1,
        UserData=startup_script
    )

    instance_id = instance["Instances"][0]["InstanceId"]
    print(f"Created instance: {instance_id}. Waiting for it to start...")

    waiter = client.get_waiter("instance_running")
    waiter.wait(InstanceIds=[instance_id])
    print(f"Instance started. Waiting for setup script to finish...")
    
    time.sleep(90)
    print(f"Setup script finished")

    return instance_id

def get_instance_public_dns_name(instance_id):
    instance = client.describe_instances(InstanceIds=[instance_id])
    instance_details = instance["Reservations"][0]["Instances"][0]
    return instance_details["PublicIpAddress"], instance_details["PublicDnsName"]

def copy_files(key_pair_name, public_dns_name, file_path, remote_path):
    print(f"Copying {file_path}...\n")
    os.system(f"scp -o StrictHostKeyChecking=no -O -i {key_pair_name}.pem -r {file_path} ubuntu@{public_dns_name}:{remote_path}")
    print(f"\nCopying {file_path}... Done")
    
def run_server(key_pair_name, public_dns_name, remote_path):
    print(f"Starting server...")
    os.system(
        f"ssh -o StrictHostKeyChecking=no -i {key_pair_name}.pem ubuntu@{public_dns_name} 'source {remote_path}/venv/bin/activate && sudo uvicorn app:app > {remote_path}/server.log 2>&1 &' &"
    )
    print(f"Starting server... Done")

def terminate_instance(instance_id):
    waiter = client.get_waiter("instance_terminated")
    waiter.wait(InstanceIds=[instance_id])

key_pair_name = os.getenv("AWS_KEY_PAIR_NAME")
security_group_name="rag-application"
remote_path = "/home/ubuntu"

def _run_command(command):
    if command == "--create-kp":
        create_and_save_key_pair(key_pair_name)
        return 0
    
    elif command == "--create-sg":
        create_security_group(security_group_name)
        return 0

    elif command == "--create":
        instance_id = create_and_run_instance(key_pair_name, security_group_name)
        with open("instance_id.txt", "w") as file:
            file.write(instance_id)

        public_ip_address, public_dns_name = get_instance_public_dns_name(instance_id)
        with open("instance_public_ip.txt", "w") as file:
            file.write(public_ip_address)
        with open("instance_public_dns.txt", "w") as file:
            file.write(public_dns_name)

        return 0

    elif command == "--copy":
        with open("instance_id.txt", "r") as file:
            instance_id = file.read().strip()
        
        with open("instance_public_dns.txt", "r") as file:
            public_dns_name = file.read().strip()

        copy_files(key_pair_name, public_dns_name, "app.py", remote_path)
        copy_files(key_pair_name, public_dns_name, "graph_rag.py", remote_path)
        copy_files(key_pair_name, public_dns_name, "pdf_html_extractor.py", remote_path)
        copy_files(key_pair_name, public_dns_name, "requirements.txt", remote_path)
        copy_files(key_pair_name, public_dns_name, ".env", remote_path)
        return 0

    elif command == "--serve":
        with open("instance_id.txt", "r") as file:
            instance_id = file.read().strip()
        
        with open("instance_public_dns.txt", "r") as file:
            public_dns_name = file.read().strip()

        print(f"Checking if server is already running...")
        server_status = os.system(f"ssh -o StrictHostKeyChecking=no -i {key_pair_name}.pem ubuntu@{public_dns_name} 'sudo lsof -i :8000' > /dev/null")
        if server_status == 0:
            print(f"Server is already running")
            return 0
        print(f"Server is not running\n")

        run_server(key_pair_name, public_dns_name, remote_path)
        return 0

    elif command == "--unserve":
        with open("instance_id.txt", "r") as file:
            instance_id = file.read().strip()
        
        with open("instance_public_dns.txt", "r") as file:
            public_dns_name = file.read().strip()

        print(f"Checking if server is running...")
        server_status = os.system(f"ssh -o StrictHostKeyChecking=no -i {key_pair_name}.pem ubuntu@{public_dns_name} 'sudo lsof -i :8000' > /dev/null")
        if server_status != 0:
            print(f"Server is not running")
            return 0
        print(f"Server is running\n")

        print(f"Stopping server...")
        os.system(f"ssh -o StrictHostKeyChecking=no -i {key_pair_name}.pem ubuntu@{public_dns_name} 'sudo kill $(sudo lsof -t -i:8000)'")
        print(f"Stopping server... Done")
        return 0

    elif command == "--start":
        with open("instance_id.txt", "r") as file:
            instance_id = file.read().strip()

        print(f"Starting instance: {instance_id}")
        client.start_instances(InstanceIds=[instance_id])

        waiter = client.get_waiter("instance_running")
        waiter.wait(InstanceIds=[instance_id])
        print(f"Instance started")

        public_ip_address, public_dns_name = get_instance_public_dns_name(instance_id)
        with open("instance_public_ip.txt", "w") as file:
            file.write(public_ip_address)
        with open("instance_public_dns.txt", "w") as file:
            file.write(public_dns_name)

        return 0

    elif command == "--stop":
        with open("instance_id.txt", "r") as file:
            instance_id = file.read().strip()

        print(f"Stopping instance: {instance_id}")
        client.stop_instances(InstanceIds=[instance_id])
        waiter = client.get_waiter("instance_stopped")
        waiter.wait(InstanceIds=[instance_id])
        print(f"Instance stopped")
        return 0

    elif command == "--describe":
        with open("instance_id.txt", "r") as file:
            instance_id = file.read().strip()
            print(f"Instance ID: {instance_id}")

        with open("instance_public_dns.txt", "r") as file:
            public_dns_name = file.read().strip()
            print(f"Public DNS Name: {public_dns_name}")

        with open("instance_public_ip.txt", "r") as file:
            public_ip_address = file.read().strip()
            print(f"Public IP Address: {public_ip_address}")
            print(f"Search engine is running at http://{public_ip_address}:8000")
        
        return 0

    elif command == "--kill":
        with open("instance_id.txt", "r") as file:
            instance_id = file.read().strip()
            client.terminate_instances(InstanceIds=[instance_id])
        terminate_instance(instance_id)

        os.remove("instance_id.txt")
        os.remove("instance_public_dns.txt")
        os.remove("instance_public_ip.txt")

        return 0

    else:
        print("Invalid argument")
        print("Usage: python deploy.py [< --create-kp, --create-sg, --create, --copy, --serve, --unserve, --start, --stop, --describe, --kill >]")
        return 1

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 0:
        print("Usage: python deploy.py [< --create-kp, --create-sg, --create, --copy, --serve, --unserve, --start, --stop, --describe, --kill >]")
        sys.exit(1)

    for command in args:
        status = _run_command(command)
        if status != 0:
            sys.exit(1)

    sys.exit(0)
    
        