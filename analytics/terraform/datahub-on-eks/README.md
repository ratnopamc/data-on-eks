# Deploying DataHub on EKS
Checkout the [documentation website](https://awslabs.github.io/data-on-eks/docs/blueprints/data-analytics/datahub-on-eks) to deploy this pattern and run sample tests.


## Release Notes

### Version 1.1.0 (June 2025)

#### EKS Cluster Upgrade
- Updated Kubernetes version from 1.31 to 1.33 (latest available)
- Upgraded node group instance types from m5.xlarge to m7g.xlarge (AWS Graviton3)

#### DataHub Components Upgrade
- Updated DataHub Helm chart from version 0.5.10 to 0.6.8 (with appVersion v1.1.0)
- Added explicit image tags (v1.1.0) for all DataHub components
- Updated DataHub version references from v0.15.0.1 to v1.1.0

#### AWS Services Upgrade
- OpenSearch: Updated from 2.11 to 2.19
- MSK Kafka: Updated from 3.8.x to 3.9.x
- RDS MySQL: Updated from 8.0 to 8.4.5
- Instance types: Upgraded from m6g/c6g to m7g/c7g for better performance

#### Provider and Module Versions
- AWS provider: Updated from >= 3.72 to >= 5.0.0
- Helm provider: Updated from >= 2.4.1 to >= 2.10.0
- Kubernetes provider: Updated from >= 2.10 to >= 2.23.0
- Random provider: Updated from >= 3.1 to >= 3.5.0
- Various module versions updated to latest

## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.3.2 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 5.95 |
| <a name="requirement_helm"></a> [helm](#requirement\_helm) | ~> 2.17 |
| <a name="requirement_kubernetes"></a> [kubernetes](#requirement\_kubernetes) | >= 2.10 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | ~> 5.95 |
| <a name="provider_kubernetes"></a> [kubernetes](#provider\_kubernetes) | >= 2.10 |


## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_datahub"></a> [datahub](#module\_datahub) | ./datahub-addon | n/a |
| <a name="module_ebs_csi_driver_irsa"></a> [ebs\_csi\_driver\_irsa](#module\_ebs\_csi\_driver\_irsa) | terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks | ~> 5.30 |
| <a name="module_eks"></a> [eks](#module\_eks) | terraform-aws-modules/eks/aws | ~> 19.21 |
| <a name="module_eks_blueprints_addons"></a> [eks\_blueprints\_addons](#module\_eks\_blueprints\_addons) | aws-ia/eks-blueprints-addons/aws | ~> 1.13 |
| <a name="module_vpc"></a> [vpc](#module\_vpc) | terraform-aws-modules/vpc/aws | ~> 5.5 |
| <a name="module_vpc_endpoints"></a> [vpc\_endpoints](#module\_vpc\_endpoints) | terraform-aws-modules/vpc/aws//modules/vpc-endpoints | ~> 5.5 |


## Resources

| Name | Type |
|------|------|
| [aws_availability_zones.available](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/availability_zones) | data source |
| [aws_eks_cluster_auth.this](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/eks_cluster_auth) | data source |
| [kubernetes_ingress_v1.datahub_datahub_frontend](https://registry.terraform.io/providers/hashicorp/kubernetes/latest/docs/data-sources/ingress_v1) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_create_vpc"></a> [create\_vpc](#input\_create\_vpc) | Create VPC | `bool` | `true` | no |
| <a name="input_eks_cluster_version"></a> [eks\_cluster\_version](#input\_eks\_cluster\_version) | EKS Cluster version | `string` | `"1.33"` | no |
| <a name="input_enable_vpc_endpoints"></a> [enable\_vpc\_endpoints](#input\_enable\_vpc\_endpoints) | Enable VPC Endpoints | `bool` | `false` | no |
| <a name="input_name"></a> [name](#input\_name) | Name of the VPC and EKS Cluster | `string` | `"datahub-on-eks"` | no |
| <a name="input_private_subnet_ids"></a> [private\_subnet\_ids](#input\_private\_subnet\_ids) | Ids for existing private subnets - needed when create\_vpc set to false | `list(string)` | `[]` | no |
| <a name="input_private_subnets"></a> [private\_subnets](#input\_private\_subnets) | Private Subnets CIDRs. 32766 Subnet1 and 16382 Subnet2 IPs per Subnet | `list(string)` | <pre>[<br/>  "10.1.0.0/17",<br/>  "10.1.128.0/18"<br/>]</pre> | no |
| <a name="input_public_subnets"></a> [public\_subnets](#input\_public\_subnets) | Public Subnets CIDRs. 62 IPs per Subnet | `list(string)` | <pre>[<br/>  "10.1.255.128/26",<br/>  "10.1.255.192/26"<br/>]</pre> | no |
| <a name="input_region"></a> [region](#input\_region) | Region | `string` | `"us-west-2"` | no |
| <a name="input_tags"></a> [tags](#input\_tags) | Default tags | `map(string)` | `{}` | no |
| <a name="input_vpc_cidr"></a> [vpc\_cidr](#input\_vpc\_cidr) | VPC CIDR - must change to match the cidr of the existing VPC if create\_vpc set to false | `string` | `"10.1.0.0/16"` | no |
| <a name="input_vpc_id"></a> [vpc\_id](#input\_vpc\_id) | VPC Id for the existing vpc - needed when create\_vpc set to false | `string` | `""` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_cluster_arn"></a> [cluster\_arn](#output\_cluster\_arn) | The Amazon Resource Name (ARN) of the cluster |
| <a name="output_cluster_name"></a> [cluster\_name](#output\_cluster\_name) | The Amazon Resource Name (ARN) of the cluster |
| <a name="output_configure_kubectl"></a> [configure\_kubectl](#output\_configure\_kubectl) | Configure kubectl: make sure you're logged in with the correct AWS profile and run the following command to update your kubeconfig |
| <a name="output_frontend_url"></a> [frontend\_url](#output\_frontend\_url) | URL for datahub frontend |
| <a name="output_oidc_provider_arn"></a> [oidc\_provider\_arn](#output\_oidc\_provider\_arn) | The ARN of the OIDC Provider if `enable_irsa = true` |


## Authentication

DataHub is configured with authentication enabled for both backend and frontend components:

- **Default Admin User**: `datahub`
- **Password Retrieval**: `kubectl get secret datahub-user-secret -n datahub -o jsonpath='{.data.*}' | base64 -d`
- **Session Timeout**: 8 hours
- **Token Expiration**: 24 hours

After deployment, access the DataHub frontend URL and login with the default admin credentials to start using the platform.
