import os
import time
import json
import yaml
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    ManagedOnlineEndpoint,
    ManagedOnlineDeployment,
)

class HuggingFace():
    def __init__(self,
                 config_file: str = 'config.yml',):
        ## Prepare config file
        self.config_file = config_file
        self.load_config()
        ## Azure basic configuraion
        self.subscription_id = self.config['Azure']['subscription_id']
        self.resource_group = self.config['Azure']['resource_group']
        self.client_id = self.config['Azure']['identity']['client_id']
        self.ml_client = None  ## initialization
        ## AML configuraion
        self.workspace_name = self.config['Azure']['ml']['workspace_name']
        self.instance_type = self.config['Azure']['ml']['compute']['instance_type']
        self.instance_count = self.config['Azure']['ml']['compute']['instance_count']
        ## HuggingFace configuraion
        self.registry_name = self.config['Model']['registry_name']
        self.model_name = self.config['Model']['model_name']
        self.model_id = f"azureml://registries/{self.registry_name}/models/{self.model_name}/labels/latest"
        ## Endpoint name
        self.endpoint_name = self.config['API']['endpoint_name']
        self.deployment_name = self.config['API']['deployment_name']

    def load_config(self):
        '''
        Load and extract config yml file.
        '''
        try:
            with open(self.config_file) as file:
                self.config = yaml.safe_load(file)
        except Exception as e:
            print(e)
            raise

    def credentialManagedID(self) -> None:
        '''
        This method is used to authenticate using managed identity.
        Specify the client ID of the managed identity in the environment variable AZURE_CLIENT_ID.
        '''
        try:
            self.credential = DefaultAzureCredential(managed_identity_client_id=self.client_id)
            self.credential.get_token("https://management.azure.com/.default")
        except Exception as e:
            print(e)

    def configureMLClient(self) -> None:
        '''
        This method is used to configure Azure ML workspace.
        '''
        self.credentialManagedID()
        ## Get MLClient
        try:
            self.ml_client = MLClient.from_config(credential=self.credential)
        except Exception as e:
            client_config = {
                            "subscription_id": self.subscription_id,
                            "resource_group": self.resource_group,
                            "workspace_name": self.workspace_name,
                        }
            config_path = "../.azureml/config.json"
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, "w") as fo:
                fo.write(json.dumps(client_config))
            self.ml_client = MLClient.from_config(credential=self.credential, path=config_path)


    def configEndpoint(self) -> None:
        '''
        Configuration in populating Endpoint
        '''
        try:
            print('Start configuring the endpoint')
            self.ml_client.begin_create_or_update(ManagedOnlineEndpoint(name=self.endpoint_name) ).wait()
            print('Endpoint is configured')
        except Exception as e:
            print(e)

    def configDeployment(self) -> None:
        '''
        Configuration in populating Deployment after Endpoint is configured
        '''
        try:
            print('Start configuring the deployment')
            self.ml_client.online_deployments.begin_create_or_update(ManagedOnlineDeployment(name=self.deployment_name,
                                                                          endpoint_name=self.endpoint_name,
                                                                          model=self.model_id,
                                                                          instance_type=self.instance_type,
                                                                          instance_count=self.instance_count,
                                                                          )).wait()
            print('Deployment is configured')
        except Exception as e:
            print(e)

    def consumeEndpoint(self,
                        message: str) -> list:
        '''
        Make sure the results with deployment
        '''
        try:
            ## tmp file in consuming API
            scoring_file = "./sample_score.json"
            with open(scoring_file, "w") as outfile:
                outfile.write('{"inputs": "' + message + '"}')
            ## Invoke endpoint
            response = self.ml_client.online_endpoints.invoke(
                endpoint_name=self.endpoint_name,
                deployment_name=self.deployment_name,
                request_file=scoring_file,
            )
            response_json = json.loads(response)
            return json.dumps(response_json, indent=2)
        except Exception as e:
            print(e)