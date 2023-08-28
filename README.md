# AzureML_HuggingFace

This repository intends to guide how we populate HuggingFace API with pre-defined models in Azure ML with sample codes. You find [the basic description](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-use-foundation-models?view=azureml-api-2).

## Assumption
- The following Azure resources are already provisioned:
    - Azure ML and related resources
    - [User managed identity](https://learn.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview)
    - python environment is prepared with [these libraries](./requirements.txt). This repository was tested with python 3.9.

- Configuration prequisites: Please prepare the following contents for configuration as `./config.yml`.

```yml
Model:
    registry_name: 'HuggingFace'
    model_name: 'bert-base-multilingual-uncased' ## Please find appropriate model in Model Catalogue in Azure ML

Azure:
    subscription_id: <YOUR SUBSCRIPTION ID in AZURE>
    resource_group: <YOUR RESOURCE GROUP>
    identity:
        client_id: <YOUR MANAGED IDENTITY> ## You may change the way of authentication such as service principal. In such a case, you need to modify the method `credentialManagedID` in ./src/utils.py
    ml:
        workspace_name: <YOUR AZURE ML WORKSPACE NAME>
        compute:
            instance_type: "Standard_DS2_v2"
            instance_count: 1

API:
    endpoint_name: <ENDPOINT NAME>
    deployment_name: <DEPLOYMENT NAME>
```

## How to use
- Please follow the instruction in [how-to-use.ipynb](./notebook/how-to-use.ipynb), which refers to [the script](./src/utils.py).

## Basic features
- Used `manated identity` for `Entra ID`(`Azure AD`) authentication in consuming populated Endpoints.






