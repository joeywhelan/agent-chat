# Custom Routing Demo
## Contents
1.  [Summary](#summary)
2.  [Presentation](#presentation)
3.  [Architecture](#architecture)
4.  [Features](#features)
5.  [Prerequisites](#prerequisites)
6.  [Installation](#installation)
7.  [Usage](#usage)

## Summary <a name="summary"></a>
This how Elasticsearch data can be queried via natural language in two different models:
- Elastic AI Agent within Kibana
- Claude Code enabled with Elasticsearch skills

## Presentation <a name="presentation"></a>
https://joeywhelan.github.io/agent-chat/

## Architecture <a name="architecture"></a>
![architecture](assets/images/arch.png) 

## Features <a name="features"></a>
- Jupyter notebook
- Builds an Elastic Cloud Hosted (ECH) deployment via Terraform
- Creates a synthetic data set of product orders
- Demonstrates natural language queries from Kibana and Claude Code
- Deletes the entire deployment via Terraform

## Prerequisites <a name="prerequisites"></a>
- uv
- terraform
- Elastic Cloud account and API key
- Python

## Installation <a name="installation"></a>
- Edit the terraform.tfvars.sample and rename to terraform.tfvars
- Create a Python virtual environment

## Usage <a name="usage"></a>
- Execute notebook