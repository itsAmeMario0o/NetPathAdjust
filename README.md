# Prepare and configure TGW attachment for MCD Centralized Deployment in AWS

## Prerequisites
Make sure you have AWS credentials configured(aws cli configure) with privileges to provision the required AWS resources.

This script will document VPCs, Route Tables, and TGWs to update TGW attachements. Will also generate terraform for the items in question so they may be merged and imported into an exisiting deployment.