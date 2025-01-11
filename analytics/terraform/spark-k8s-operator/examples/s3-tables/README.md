# S3Table with OSS Spark on EKS Guide

This guide provides step-by-step instructions for setting up and running a Spark job on Amazon EKS using S3Table for data storage.

## Prerequisites

- Latest version of AWS CLI installed (must include S3Tables API support)

## Step 1: Deploy Spark Cluster on EKS

Follow the steps to deploy Spark Cluster on EKS

[Spark Operator on EKS with YuniKorn Scheduler](https://awslabs.github.io/data-on-eks/docs/blueprints/data-analytics/spark-operator-yunikorn#prerequisites)

Once your cluster is up and running, proceed with the following steps to execute a sample Spark job using S3Tables.

## Step 2: Create Test Data for the job

Navigate to the example directory and Generate sample data:

```sh
cd analytics/terraform/spark-k8s-operator/examples/s3-tables
./input-data-gen.sh
```

This will create a file called `employee_data.csv` locally with 100 records. Modify the script to adjust the number of records as needed.

## Step 3: Upload Test Input data to your S3 Bucket

Replace `<YOUR_S3_BUCKET>` with the name of the S3 bucket created by your blueprint and run the below command.

```sh
aws s3 cp employee_data.csv s3://<S3_BUCKET>/s3table-example/input/
```

## Step 4: Upload PySpark Script to S3 Bucket

Replace `<S3_BUCKET>` with the name of the S3 bucket created by your blueprint and run the below command to upload sample Spark job to S3 buckets.

```sh
aws s3 cp s3table-iceberg-pyspark.py s3://<S3_BUCKET>/s3table-example/scripts/
```

## Step 5: Create S3Table

Replace <REGION> and <S3TABLE_BUCKET_NAME> with desired names.

```sh
aws s3tables create-table-bucket \
    --region "<REGION>" \
    --name "<S3TABLE_BUCKET_NAME>"
```

Make note of the S3TABLE ARN generated by this command.

## Step 6: Update Spark Operator YAML File

 - Open `s3table-spark-operator.yaml` file in your preferred text editor.
 - Replace `<S3_BUCKET>` with your S3 bucket created by this blueprint(Check Terraform outputs). S3 Bucket where you copied test data and sample spark job in the above steps.
 - REPLACE `<S3TABLE_ARN>` with your S3 Table ARN.

## Step 7: Execute Spark Job

Apply the updated YAML file to your Kubernetes cluster to submit the Spark Job.

```sh
cd analytics/terraform/spark-k8s-operator/examples/s3-tables
kubectl apply -f s3table-spark-operator.yaml
```

## Step 8: Verify the Spark Driver log for the output

Check the Spark driver logs to verify job progress and output:

```sh
kubectl logs <spark-driver-pod-name> -n spark-team-a
```

## Step 9: Verify the S3Table using S3Table API

Use the S3Table API to confirm the table was created successfully. Just replace the `<ACCOUNT_ID>` and run the command.

```sh
aws s3tables get-table --table-bucket-arn arn:aws:s3tables:us-west-2:<ACCOUNT_ID>:bucket/doeks-spark-on-eks-s3table --namespace doeks_namespace --name employee_s3_table
```

Output looks like below.

```json
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

Monitor the table maintenance job status:

```sh
aws s3tables get-table-maintenance-job-status --table-bucket-arn arn:aws:s3tables:us-west-2:<ACCOUNT_ID>:bucket/doeks-spark-on-eks-s3table --namespace doeks_namespace --name employee_s3_table
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

## Step10: Clean up

Delete the table.

```bash
aws s3tables delete-table \
  --namespace doeks_namespace \
  --table-bucket-arn ${S3TABLE_ARN} \
  --name employee_s3_table
```

Delete the namespace.

```bash
aws s3tables delete-namespace \
  --namespace doeks_namespace \
  --table-bucket-arn ${S3TABLE_ARN}
```

Finally, delete the bucket table

```bash
aws s3tables delete-table-bucket \
  --region "<REGION>" \
  --table-bucket-arn ${S3TABLE_ARN}
```


# Conclusion
You have successfully set up and run a Spark job on Amazon EKS using S3Table for data storage. This setup provides a scalable and efficient way to process large datasets using Spark on Kubernetes with the added benefits of S3Table's data management capabilities.

For more advanced usage, refer to the official AWS documentation on S3Table and Spark on EKS.