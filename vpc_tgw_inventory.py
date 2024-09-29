import boto3
from prettytable import PrettyTable

# Initialize AWS clients
ec2_client = boto3.client('ec2')
tgw_client = boto3.client('ec2')

def list_vpcs():
    response = ec2_client.describe_vpcs()
    vpcs = response['Vpcs']
    table = PrettyTable(['Index', 'VPC ID', 'CIDR Block', 'State'])
    for index, vpc in enumerate(vpcs):
        table.add_row([index, vpc['VpcId'], vpc['CidrBlock'], vpc['State']])
    print(table)
    return vpcs

def list_transit_gateways():
    response = tgw_client.describe_transit_gateways()
    tgws = response['TransitGateways']
    table = PrettyTable(['Index', 'TGW ID', 'Description', 'State'])
    for index, tgw in enumerate(tgws):
        table.add_row([index, tgw['TransitGatewayId'], tgw.get('Description', 'N/A'), tgw['State']])
    print(table)
    return tgws

def list_subnets(vpc_id):
    response = ec2_client.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    subnets = response['Subnets']
    table = PrettyTable(['Index', 'Subnet ID', 'CIDR Block', 'Availability Zone'])
    for index, subnet in enumerate(subnets):
        table.add_row([index, subnet['SubnetId'], subnet['CidrBlock'], subnet['AvailabilityZone']])
    print(table)
    return subnets

def list_route_tables(vpc_id):
    response = ec2_client.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    route_tables = response['RouteTables']
    table = PrettyTable(['Index', 'Route Table ID'])
    for index, rt in enumerate(route_tables):
        table.add_row([index, rt['RouteTableId']])
    print(table)
    return route_tables

def create_tgw_attachment(tgw_id, vpc_id, subnet_ids):
    response = tgw_client.create_transit_gateway_vpc_attachment(
        TransitGatewayId=tgw_id,
        VpcId=vpc_id,
        SubnetIds=subnet_ids
    )
    return response['TransitGatewayVpcAttachment']

def update_route_table(route_table_id, destination_cidr, tgw_id):
    ec2_client.create_route(
        RouteTableId=route_table_id,
        DestinationCidrBlock=destination_cidr,
        TransitGatewayId=tgw_id
    )

def generate_terraform_script(tgw_id, vpc_id, subnet_ids, route_table_id, destination_cidr):
    terraform_script = f"""
provider "aws" {{
  region = "us-west-2"
}}

resource "aws_ec2_transit_gateway_vpc_attachment" "example" {{
  transit_gateway_id = "{tgw_id}"
  vpc_id             = "{vpc_id}"
  subnet_ids         = {subnet_ids}
}}

resource "aws_route" "example" {{
  route_table_id         = "{route_table_id}"
  destination_cidr_block = "{destination_cidr}"
  transit_gateway_id     = "{tgw_id}"
}}
"""
    with open('main.tf', 'w') as file:
        file.write(terraform_script)
    print("Terraform script generated: main.tf")

def main():
    print("Listing all VPCs:")
    vpcs = list_vpcs()
    vpc_index = int(input("Enter the index of the VPC to attach to the Transit Gateway: "))
    vpc_id = vpcs[vpc_index]['VpcId']

    print("Listing all Transit Gateways:")
    tgws = list_transit_gateways()
    tgw_index = int(input("Enter the index of the Transit Gateway to attach the VPC to: "))
    tgw_id = tgws[tgw_index]['TransitGatewayId']

    print(f"Listing subnets for VPC {vpc_id}:")
    subnets = list_subnets(vpc_id)
    subnet_indices = input("Enter the indices of the Subnet IDs to associate with the Transit Gateway (comma-separated): ").split(',')
    subnet_ids = [subnets[int(index)]['SubnetId'] for index in subnet_indices]

    print("Creating Transit Gateway Attachment...")
    attachment = create_tgw_attachment(tgw_id, vpc_id, subnet_ids)
    print(f"Transit Gateway Attachment created: {attachment['TransitGatewayAttachmentId']}")

    print("Listing all VPCs again for destination selection:")
    vpcs = [vpc for vpc in vpcs if vpc['VpcId'] != vpc_id]
    table = PrettyTable(['Index', 'VPC ID', 'CIDR Block', 'State'])
    for index, vpc in enumerate(vpcs):
        table.add_row([index, vpc['VpcId'], vpc['CidrBlock'], vpc['State']])
    print(table)
    destination_vpc_index = int(input("Enter the index of the destination VPC: "))
    destination_vpc_id = vpcs[destination_vpc_index]['VpcId']

    print(f"Listing subnets for destination VPC {destination_vpc_id}:")
    destination_subnets = list_subnets(destination_vpc_id)
    destination_subnet_index = int(input("Enter the index of the destination subnet: "))
    destination_cidr = destination_subnets[destination_subnet_index]['CidrBlock']

    print(f"Listing route tables for VPC {vpc_id}:")
    route_tables = list_route_tables(vpc_id)
    route_table_index = int(input("Enter the index of the Route Table to update: "))
    route_table_id = route_tables[route_table_index]['RouteTableId']

    print("Updating Route Table...")
    update_route_table(route_table_id, destination_cidr, tgw_id)
    print("Route Table updated.")

    print("Generating Terraform script...")
    generate_terraform_script(tgw_id, vpc_id, subnet_ids, route_table_id, destination_cidr)

if __name__ == "__main__":
    main()