# k8s-node-doctor

# If your cluster nodes are not feeling well - You need a doctor (k8s-node-doctor) immediately!!

According to hospital insurance codes, there are 9 different ways you can be injured by turtles - Wall Street Journal.

But in the Kubernetes Eco-System, there are 1000 ways - Ravi

To ensure your operations are smooth -  Please clone this repo as soon as possible :)

Node Doctor will run some check/s to ensure a worker node is operating as swiftly as possible. 

## Problem: 

Don't you want to do a pre-check before you onboard any application to your cluster? What would you do, if your applications are not being able to connect to dependent services like consul, Kafka clusters, etc. from the new nodes that were added to the cluster to increase the capacity? 

## Solution

To mitigate the above issue concerning connectivity for the new nodes in any cluster, we have an application now to do these connectivity checks in a scheduled manner.  

In this iteration(v1.0.0), I have created a containerized python application that can run on every node in a Kubernetes cluster to perform connectivity checks to the underlying sub-systems like a vault, Redis, Kafka clusters, etc.

I have used AdvancedCronJob, which is an enhanced version of CronJob. The original CronJob creates Job periodically according to schedule rule, but AdvancedCronJob provides template support for multiple job resources like jobTemplate and batchJobTemplate.

More information is here - https://openkruise.io/en-us/docs/advancedcronjob.html

Using AdvancedCronJob, we can create a BroadcastJob that can be run on every node where the execution can be scheduled periodically.

## Prerequisities 

- Kubernetes Cluster with version >= 1.19
- openkruise installed v0.9.0
- worker nodes (nodes) with docker installed on them 

## Usage: 

There are a couple of ways to use this application - 

1) Run this as a docker container on the nodes before adding them to the cluster. 
   - you need Docker installed on the node (pre-requisite) 
   - you should be able to pull the k8s-node-doctor docker image from the golden repo (pre-requisite)
     docker pull <docker-hub>
   - Update the endpoints.yaml file in the github repo under the endpoints/<ENV> folder and create a pull request for someone to review the endpoint details. Once it is merged, you are good to use the application.
   - this will send the notification to the slack channel (#<name of your slack channel>). 
     
     You can run this command with appropriate parameters as shown below as an example. 
   

            docker run -e MY_NODE_NAME=<YOUR NODE NAME> -e CLUSTER_NAME=<CLUSTER NAME> -e SLACK_ENABLED=<true/false> -e EMAIL_ENABLED=<true/false> -e DC_NUMBER=<DC NUMBER> <image:tag>
   
 2) This application can be deployed on any cluster using app-of-apps (Please check under kustomize/overlays/ in this repo). 
  

The output format in slack ensures that -

- Failed hosts information is displayed first, followed by the successful connections information.
- If a host has multiple ports to be tested, the connection result will display all ports separated by a comma in the same line.
   
 
# Limitations and known issues - 

 1) As of now, only Slack is configured for sending notifications. E-mail is not yet enabled.   
 2) Endpoint.yaml standard format should be followed which means grouping hostnames under some key/pillar is desired. Recently we found a bug when no hosts were defined under the pillar. It is now fixed. Now you can have pillar object empty i.e. no hostnames required in every pillar.
 3) If you are using the FQDN for the host, make sure that it is resolvable. If not, the application will break while handling that particular host and will not continue the execution.
 4) Since we are using OpenKruise's CRD of advancedcronjob, you will be able to deploy an updated version of the application but it won't be in sync with ArgoCD.   
 
            apps.kruise.io/v1alpha1/AdvancedCronJob -  SyncFailed
            admission webhook "vadvancedcronjob.kb.io" denied the request: spec: Forbidden: updates to advancedcronjob spec for fields other than 'schedule', 'concurrencyPolicy', 'successfulJobsHistoryLimit', 'failedJobsHistoryLimit', 'startingDeadlineSeconds' and 'paused' are forbidden
          
 As a result, image tag changes will not take effect unless you delete the whole application. 
 

# Note 
 This repo will evolve with multiple applications (in the future) that can ease work for Platform and App operations teams.

# Jenkins job to push the image to Golden repo 
  
# Jenkins Job to push the image to Public Endpoint registry 

