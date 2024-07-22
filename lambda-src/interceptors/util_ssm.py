from aws_lambda_powertools.utilities import parameters
from botocore.config import Config

config = Config(region_name="us-east-1")
ssm_provider = parameters.SSMProvider(config=config)
