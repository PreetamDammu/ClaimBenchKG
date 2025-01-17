import boto3
import json
import logging
import time

from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def build_anthropic_request_body(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    temperature: float = 1.0
) -> dict:
    """
    Builds the JSON payload for Anthropic Claude.

    :param system_prompt: Instructions or context for the system.
    :param user_prompt: The text of the user's request.
    :param max_tokens: The maximum number of tokens to generate.
    :param temperature: Sampling temperature (creativity control).
    :return: A dict representing the request body for Claude.
    """
    # For Anthropic on Bedrock, the required fields typically include:
    # - anthropic_version
    # - system (system instructions)
    # - messages (the conversation so far)
    # - max_tokens (or max_tokens_to_sample in older versions)
    # - Optionally: temperature, top_p, etc.

    # Note: If your particular Claude model expects a single combined prompt,
    # you can instead pass a single string in "prompt". This example uses
    # "system" and "messages" to reflect the multi-message format.
    

    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    return request_body


def invoke_bedrock_endpoint(
    request_body: dict,
    model_id: str,
    region_name: str = "us-east-1",
    max_retries: int = 3,
    backoff_factor: float = 2.0
) -> dict:
    """
    Invokes the Bedrock endpoint with a given request body and model ID,
    with exponential backoff retries for transient errors.

    :param request_body: JSON payload specific to the chosen model.
    :param model_id: The Bedrock model ID, e.g. "anthropic.claude-v1".
    :param region_name: The AWS region to call. Default is "us-east-1".
    :param max_retries: Number of retry attempts for transient errors.
    :param backoff_factor: Factor for exponential backoff, e.g. 2.0 means
                           1s, 2s, 4s between retries, etc.
    :return: The deserialized JSON response from Bedrock.
    """
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        region_name=region_name
    )

    for attempt in range(max_retries):
        try:
            # Serialize the request body as JSON.
            body_json = json.dumps(request_body)

            response = bedrock_runtime.invoke_model(
                body=body_json,
                modelId=model_id,
                contentType='application/json'
            )

            # The response body is a StreamingBody, so we need to read and decode it.
            response_body = json.loads(response.get('body').read())
            return response_body

        except ClientError as err:
            logger.error(
                "Error invoking Bedrock on attempt %s: %s",
                attempt + 1,
                err.response["Error"]["Message"]
            )

            # If this was the last attempt, re-raise the error.
            if attempt == max_retries - 1:
                raise

            # Otherwise, back off exponentially before retrying.
            sleep_time = backoff_factor ** attempt
            logger.info(f"Retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)
