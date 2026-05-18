# AI-assisted: reviewed by [name]
"""
BedrockProvider — Llama 3.1 via AWS Bedrock.

boto3 is optional: if not installed, imports still succeed but
generate() raises a clear error so the caller can fall back gracefully.
Switch provider via: LLM_PROVIDER=bedrock
"""
import json
import time

try:
    import boto3
    _BOTO3_AVAILABLE = True
except ImportError:
    _BOTO3_AVAILABLE = False

from ai.config.settings import (
    BEDROCK_MODEL,
    BEDROCK_REGION,
    MAX_OUTPUT_TOKENS,
    TEMPERATURE,
)
from .base import LlmProvider, LlmProviderError, LlmResponse


class BedrockProvider(LlmProvider):
    name = "bedrock"

    def generate(self, system_prompt: str, user_prompt: str) -> LlmResponse:
        if not _BOTO3_AVAILABLE:
            raise LlmProviderError(
                "boto3 is not installed. Run: pip install boto3==1.34.84"
            )
        client = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)
        # Llama 3 on Bedrock uses the converse API with a messages format.
        body = json.dumps({
            "prompt": f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n{user_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>",
            "max_gen_len": MAX_OUTPUT_TOKENS,
            "temperature": TEMPERATURE,
        })
        t0 = time.monotonic()
        try:
            response = client.invoke_model(
                modelId=BEDROCK_MODEL,
                body=body,
                contentType="application/json",
                accept="application/json",
            )
        except Exception as exc:
            raise LlmProviderError(f"Bedrock invocation failed: {exc}") from exc

        latency_ms = int((time.monotonic() - t0) * 1000)
        result = json.loads(response["body"].read())
        text = result.get("generation", "").strip()

        return LlmResponse(
            text=text,
            model=BEDROCK_MODEL,
            provider="bedrock",
            latency_ms=latency_ms,
            tokens_in=result.get("prompt_token_count"),
            tokens_out=result.get("generation_token_count"),
            raw=result,
        )

    def health_check(self) -> bool:
        if not _BOTO3_AVAILABLE:
            return False
        try:
            session = boto3.Session()
            creds = session.get_credentials()
            if creds is None:
                return False
            # Construct the client without making an API call.
            boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)
            return True
        except Exception:
            return False
