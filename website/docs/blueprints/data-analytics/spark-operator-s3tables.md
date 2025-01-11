---
sidebar_position: 3
sidebar_label: S3 Tables on EKS
hide_table_of_contents: true
---
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';
import CollapsibleContent from '../../../src/components/CollapsibleContent';

import TaxiTripExecute from './_taxi_trip_exec.md'
import ReplaceS3BucketPlaceholders from './_replace_s3_bucket_placeholders.mdx';

import CodeBlock from '@theme/CodeBlock';

# S3 Tables on Amazon EKS with Spark Operator

## Introduction

This document provides an overview of Amazon S3 Tables, its integration with Apache Spark, and how to use Spark Operator to manage Spark applications on Kubernetes while leveraging Amazon S3 Tables.

Amazon S3 Tables allow you to store and query data directly on Amazon S3 in tabular formats such as Parquet, ORC, or CSV. They are commonly used in data lake architectures and are often paired with query engines like Apache Spark, Hive, or Presto.

## Key Features

- 🛠️ Automatic Compaction: S3 Tables implements automatic compaction, which intelligently optimizes data storage in the background by combining smaller files into larger, more efficient ones. This process reduces storage costs, improves query speed, and operates continuously without manual intervention.
  
- 🔄 Table Maintenance: It offers critical maintenance tasks like snapshot management and unreferenced file removal. This continuous optimization ensures that tables remain performant and cost-effective without manual intervention, reducing operational overhead and allowing teams to focus on data insights.

- ❄️ Apache Iceberg Support: Offers built-in support for Apache Iceberg, which simplifies managing data lakes at scale while improving query performance and reducing costs. Consider using S3 Tables for your data lake if you want to experience the following results.
  
- 🔒 Simplified Security: S3 Tables treat your tables as AWS resources, enabling fine-grained AWS Identity and Access Management (IAM) permissions at the table level. This simplifies data governance, enhances security, and makes access control more intuitive and manageable with your familiar AWS services.

- ⚡ Enhanced Performance: Amazon S3 Tables introduce a new type of bucket, purpose-built for storing Apache Iceberg tables. Table buckets deliver up to 3x faster query performance and up to 10x higher transactions per second compared to storing Iceberg tables in general-purpose S3 buckets. This performance enhancement supports high-frequency updates, real-time ingestion, and more demanding workloads, ensuring scalability and responsiveness as data volumes grow.

<CollapsibleContent header={<h2><span>Deploying the Solution</span></h2>}>

In this [example](https://github.com/awslabs/data-on-eks/tree/main/analytics/terraform/spark-k8s-operator), you will provision the following resources required to run Spark Jobs with open source Spark Operator and Apache YuniKorn.

This example deploys an EKS Cluster running the Spark K8s Operator into a new VPC.

- Creates a new sample VPC, 2 Private Subnets, 2 Public Subnets, and 2 subnets in the RFC6598 space (100.64.0.0/10) for EKS Pods.
- Creates Internet gateway for Public Subnets and NAT Gateway for Private Subnets
- Creates EKS Cluster Control plane with public endpoint (for demo reasons only) with Managed Node Groups for benchmarking and core services, and Karpenter NodePools for Spark workloads.
- Deploys Metrics server, Spark-operator, Apache Yunikorn, Karpenter, Cluster Autoscaler, Grafana, AMP and Prometheus server.

### Prerequisites

Ensure that you have installed the following tools on your machine.

1. [aws cli](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
2. [kubectl](https://Kubernetes.io/docs/tasks/tools/)
3. [terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli)

### Deploy

Clone the repository.

```bash
git clone https://github.com/awslabs/data-on-eks.git
cd data-on-eks
export DOEKS_HOME=$(pwd)
```

If DOEKS_HOME is ever unset, you can always set it manually using `export
DATA_ON_EKS=$(pwd)` from your data-on-eks directory.

Navigate into one of the example directories and run `install.sh` script.

```bash
cd ${DOEKS_HOME}/analytics/terraform/spark-k8s-operator
chmod +x install.sh
./install.sh
```

Now create an S3_BUCKET variable that holds the name of the bucket created
during the install. This bucket will be used in later examples to store output
data. If S3_BUCKET is ever unset, you can run the following commands again.

```bash
export S3_BUCKET=$(terraform output -raw s3_bucket_id_spark_history_server)
echo $S3_BUCKET
```

</CollapsibleContent>

## Execute Sample Spark job

### Step 1: Create the S3 Tables compatible Apache Spark Docker Image

For the purposes of this blueprint, we've already provided a docker image that's publicly available.

### Step 2: Create Test Data for the job

Navigate to the example directory and Generate sample data:

```sh
cd analytics/terraform/spark-k8s-operator/examples/s3-tables
./input-data-gen.sh
```

This will create a file called employee_data.csv locally with 100 records. Modify the script to adjust the number of records as needed.

### Step 3: Upload Test Input data to Amazon S3 Bucket

Replace "\<YOUR_S3_BUCKET>" with the name of the S3 bucket created by your blueprint and run the below command.

```bash
aws s3 cp employee_data.csv s3://<S3_BUCKET>/s3table-example/input/
```

### Step 4: Upload PySpark Script to S3 Bucket

Replace S3_BUCKET with the name of the S3 bucket created by your blueprint and run the below command to upload sample Spark job to S3 buckets.

aws s3 cp s3table-iceberg-pyspark.py s3://S3_BUCKET>/s3table-example/scripts/

Navigate to example directory and submit the Spark job.

### Step 5: Create Amazon S3 Table

Replace and "\<S3TABLE_BUCKET_NAME>" with desired names.
Replace `REGION` with your AWS region.

```bash
aws s3tables create-table-bucket \
    --region "\<REGION>" \
    --name "\<S3TABLE_BUCKET_NAME>"
```

Make note of the S3TABLE ARN generated by this command.

### Step 6: Update Spark Operator YAML File

Update the Spark Operator YAML file as below:

- Open s3table-spark-operator.yaml file in your preferred text editor.
- Replace "\<S3_BUCKET> with your S3 bucket created by this blueprint(Check Terraform outputs). S3 Bucket is the place where you copied test data and sample spark job in the above steps.
- REPLACE "\<S3TABLE_ARN> with your S3 Table ARN.

### Step 7: Execute Spark Job

Apply the updated YAML file to your Kubernetes cluster to submit the Spark Job.

```bash
cd ${DOEKS_HOME}/analytics/terraform/spark-k8s-operator/examples/s3-tables
kubectl apply -f s3table-spark-operator.yaml
```

### Step 8: Verify the Spark Driver log for the output

Check the Spark driver logs to verify job progress and output:

```bash
kubectl logs <spark-driver-pod-name> -n spark-team-a
```

### Step 9: Verify the S3Table using S3Table API

Use the S3Table API to confirm the table was created successfully. Just replace the "\<ACCOUNT_ID> and run the command.

```bash
aws s3tables get-table --table-bucket-arn arn:aws:s3tables:us-west-2:<ACCOUNT_ID>:bucket/doeks-spark-on-eks-s3table --namespace doeks_namespace --name employee_s3_table
```

Output looks like below:

```text
Output looks like below.

{
    "name": "employee_s3_table",
    "type": "customer",
    "tableARN": "arn:aws:s3tables:us-west-2:<ACCOUNT_ID>:bucket/doeks-spark-on-eks-s3table/table/55511111-7a03-4513-b921-e372b0030daf",
    "namespace": [
        "doeks_namespace"
    ],
    "versionToken": "aafc39ddd462690d2a0c",
    "metadataLocation": "s3://55511111-7a03-4513-bumiqc8ihp8rnxymuhyz8t1ammu7ausw2b--table-s3/metadata/00004-62cc4be3-59b5-4647-a78d-1cdf69ec5ed8.metadata.json",
    "warehouseLocation": "s3://55511111-7a03-4513-bumiqc8ihp8rnxymuhyz8t1ammu7ausw2b--table-s3",
    "createdAt": "2025-01-07T22:14:48.689581+00:00",
    "createdBy": "<ACCOUNT_ID>",
    "modifiedAt": "2025-01-09T00:06:09.222917+00:00",
    "ownerAccountId": "<ACCOUNT_ID>",
    "format": "ICEBERG"
}
```

### Step 10: Monitor the table maintenance job status:

```bash
aws s3tables get-table-maintenance-job-status --table-bucket-arn arn:aws:s3tables:us-west-2:"\<ACCOUNT_ID>:bucket/doeks-spark-on-eks-s3table --namespace doeks_namespace --name employee_s3_table
```

This command provides information about Iceberg compaction, snapshot management, and unreferenced file removal processes.

```json
{
    "tableARN": "arn:aws:s3tables:us-west-2:<ACCOUNT_ID>:bucket/doeks-spark-on-eks-s3table/table/55511111-7a03-4513-b921-e372b0030daf",
    "status": {
        "icebergCompaction": {
            "status": "Successful",
            "lastRunTimestamp": "2025-01-08T01:18:08.857000+00:00"
        },
        "icebergSnapshotManagement": {
            "status": "Successful",
            "lastRunTimestamp": "2025-01-08T22:17:08.811000+00:00"
        },
        "icebergUnreferencedFileRemoval": {
            "status": "Successful",
            "lastRunTimestamp": "2025-01-08T22:17:10.377000+00:00"
        }
    }
}

```

<CollapsibleContent header={<h2><span>Cleanup</span></h2>}>

:::caution
To avoid unwanted charges to your AWS account, delete all the AWS resources created during this deployment
:::

## Delete the S3 Table

```bash
aws s3tables delete-table \
  --namespace doeks_namespace \
  --table-bucket-arn ${S3TABLE_ARN} \
  --name employee_s3_table
```

## Delete the namespace

```bash
aws s3tables delete-namespace \
  --namespace doeks_namespace \
  --table-bucket-arn ${S3TABLE_ARN}
```

## Delete the bucket table

```bash
aws s3tables delete-table-bucket \
  --region "<REGION>" \
  --table-bucket-arn ${S3TABLE_ARN}
```

## Delete the EKS cluster

This script will cleanup the environment using `-target` option to ensure all the resources are deleted in correct order.

```bash
cd ${DOEKS_HOME}/analytics/terraform/spark-k8s-operator && chmod +x cleanup.sh
./cleanup.sh
```

</CollapsibleContent>