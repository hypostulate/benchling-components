import os
import json
from benchling_sdk.benchling import Benchling

BENCHLING_URL = os.environ["BENCHLING_URL"]
BENCHLING_API_KEY = os.environ["BENCHLING_API_KEY"]


def lambda_handler(event, context):
    # save event to logs
    print(json.dumps(event))
    
    entity_id = event["detail"]["entity"]["id"]
    print(f"Entity with ID: {entity_id} was just registered! Wow...")

    # Get the complete entity response
    benchling = Benchling(
        url=BENCHLING_URL,
        api_key=BENCHLING_API_KEY,
    )
    entity = benchling.custom_entities.get_by_id(entity_id=entity_id)
    print(json.dumps(entity.to_dict()))

    return {
        "statusCode": 200,
        "body": {
            "entity": entity.to_dict(),
        },
    }
