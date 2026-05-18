# Cloud LLM Setup — Instructions for the AI Module

**Who this is for:** the person setting up the cloud backend so the AI chat tab
in the dashboard actually runs a real language model instead of the offline stub.

**How to use this file:** read through the whole thing once first, then go section
by section. Some steps you do manually in a browser. Other steps you hand to your
Claude Code instance — those sections are clearly marked.

---

## What you are setting up

The dashboard has an AI chat tab (Module 8). Right now it runs in offline mode
using a dummy "echo" provider that just repeats the prompt back. You are wiring
it up to a real hosted Llama 3.1 8B model so it gives actual intelligent answers
grounded in the dashboard data.

You have two options. Pick one:

| | Option A — Azure (recommended) | Option B — AWS Bedrock |
|---|---|---|
| **Free credits** | $100 free with a university email, no card needed | Needs a credit card (free tier available) |
| **New code needed** | Yes — one new file + two small edits | No — already coded |
| **Time to set up** | ~20 minutes | ~15 minutes |
| **Best if…** | You have a uni email and no AWS account | You already have an AWS account |

---

## Before you start — pull the latest code

Open a terminal in the repo folder and run:

```
git pull origin main
```

Then install dependencies:

```
pip install -r requirements.txt
```

---

## Option A — Azure AI Foundry (Student Free Plan)

### Part 1 — you do this in a browser (manual steps)

**Step 1 — activate your free Azure student account**

- Go to: https://azure.microsoft.com/en-us/free/students
- Click "Activate now"
- Sign in with your **university email address** (.ac.uk or .edu)
- Verify your student status — it's instant for most unis
- You get $100 free credit, no credit card required

**Step 2 — open Azure AI Foundry**

- Go to: https://ai.azure.com
- Sign in with the same Microsoft account
- Click "New project" — name it anything (e.g. `retail-dashboard`)
- Select or create a Hub — just accept the defaults and click through

**Step 3 — deploy the Llama model**

- In the left sidebar click **"Model catalog"**
- In the search box type: `Llama-3.1-8B-Instruct`
- Click the result — it should say "Meta" as the publisher
- Click the blue **"Deploy"** button
- Choose deployment type: **"Serverless API"** (not "Managed compute" — that's expensive)
- Region: pick **East US 2** or **West US 3** (these regions have the model available)
- Click Deploy and wait about 2 minutes

**Step 4 — copy your endpoint and key**

- Once deployed, click on the deployment to open it
- You will see two things — copy both and save them somewhere (Notepad is fine):
  - **Target URI** — looks like: `https://something.eastus2.models.ai.azure.com`
  - **Key** — a long string of letters and numbers
- Keep these private — do not commit them to GitHub

---

### Part 2 — hand this to your Claude Code (paste the instructions below)

> **Copy everything inside the box below and paste it to Claude Code as a prompt:**

---

> Read `ai/CLOUD_SETUP.md` in full before doing anything. Then carry out the following:
>
> **Task 1 — install the Azure SDK**
>
> Add this line to `requirements.txt` in the pinned-versions style already used in that file:
> ```
> azure-ai-inference==1.0.0b3
> ```
>
> **Task 2 — create the Azure provider**
>
> Create a new file `ai/providers/azure_provider.py` with the following content exactly:
>
> ```python
> # AI-assisted: reviewed by [name]
> """
> AzureProvider — Llama 3.1 via Azure AI Foundry serverless API.
>
> Required env vars:
>   AZURE_INFERENCE_ENDPOINT  — the Target URI from your Azure deployment
>   AZURE_INFERENCE_KEY       — the API key from your Azure deployment
> """
> import os
> import time
>
> from azure.ai.inference import ChatCompletionsClient
> from azure.ai.inference.models import SystemMessage, UserMessage
> from azure.core.credentials import AzureKeyCredential
>
> from ai.config.settings import MAX_OUTPUT_TOKENS, TEMPERATURE, TIMEOUT_SECONDS
> from .base import LlmProvider, LlmProviderError, LlmResponse
>
>
> class AzureProvider(LlmProvider):
>     name = "azure"
>
>     def generate(self, system_prompt: str, user_prompt: str) -> LlmResponse:
>         endpoint = os.environ.get("AZURE_INFERENCE_ENDPOINT")
>         key = os.environ.get("AZURE_INFERENCE_KEY")
>         if not endpoint or not key:
>             raise LlmProviderError(
>                 "AZURE_INFERENCE_ENDPOINT and AZURE_INFERENCE_KEY env vars must be set. "
>                 "See ai/CLOUD_SETUP.md for instructions."
>             )
>         client = ChatCompletionsClient(
>             endpoint=endpoint,
>             credential=AzureKeyCredential(key),
>         )
>         t0 = time.monotonic()
>         try:
>             resp = client.complete(
>                 messages=[
>                     SystemMessage(content=system_prompt),
>                     UserMessage(content=user_prompt),
>                 ],
>                 temperature=TEMPERATURE,
>                 max_tokens=MAX_OUTPUT_TOKENS,
>             )
>         except Exception as exc:
>             raise LlmProviderError(f"Azure inference request failed: {exc}") from exc
>
>         latency_ms = int((time.monotonic() - t0) * 1000)
>         text = resp.choices[0].message.content.strip()
>         return LlmResponse(
>             text=text,
>             model=str(resp.model),
>             provider="azure",
>             latency_ms=latency_ms,
>             tokens_in=resp.usage.prompt_tokens if resp.usage else None,
>             tokens_out=resp.usage.completion_tokens if resp.usage else None,
>             raw={},
>         )
>
>     def health_check(self) -> bool:
>         return bool(
>             os.environ.get("AZURE_INFERENCE_ENDPOINT")
>             and os.environ.get("AZURE_INFERENCE_KEY")
>         )
> ```
>
> **Task 3 — register the Azure provider in the factory**
>
> Open `ai/providers/__init__.py`. Find the block that handles `"bedrock"` (it starts with `if provider_name == "bedrock":`). Immediately after that entire block (after its closing `return EchoProvider()` line), add this new block:
>
> ```python
>     if provider_name == "azure":
>         from .azure_provider import AzureProvider
>         p = AzureProvider()
>         if p.health_check():
>             return p
>         logger.warning(
>             "Azure env vars not set (AZURE_INFERENCE_ENDPOINT / AZURE_INFERENCE_KEY). "
>             "Falling back to EchoProvider."
>         )
>         return EchoProvider()
> ```
>
> **Task 4 — verify the wiring**
>
> Run this and confirm it prints `azure`:
> ```
> AZURE_INFERENCE_ENDPOINT=https://test.example.com AZURE_INFERENCE_KEY=testkey LLM_PROVIDER=azure python -c "from ai.providers import get_provider; print(get_provider().name)"
> ```
>
> **Task 5 — run the full test suite**
>
> Run `pytest ai/tests/ -v` and confirm all 45 tests still pass. The tests use EchoProvider so no Azure credentials are needed for this step.
>
> **Task 6 — commit and push**
>
> Stage and commit only: `ai/providers/azure_provider.py`, `ai/providers/__init__.py`, `requirements.txt`.
> Commit message: `Add Azure AI Foundry provider for Llama 3.1 (Module 8)`
> Push to main.

---

### Part 3 — test the real connection (you do this)

Once Claude Code has pushed, set your credentials and run a smoke test.

**Mac / Linux:**
```bash
export AZURE_INFERENCE_ENDPOINT="https://your-endpoint-here.eastus2.models.ai.azure.com"
export AZURE_INFERENCE_KEY="your-key-here"
export LLM_PROVIDER="azure"
python -c "
from ai.services.chat_service import answer_question
r = answer_question('Which SKUs have the highest promotion lift?', 'test01')
print(r.answer)
print('label:', r.label)
"
```

**Windows PowerShell:**
```powershell
$env:AZURE_INFERENCE_ENDPOINT="https://your-endpoint-here.eastus2.models.ai.azure.com"
$env:AZURE_INFERENCE_KEY="your-key-here"
$env:LLM_PROVIDER="azure"
python -c "
from ai.services.chat_service import answer_question
r = answer_question('Which SKUs have the highest promotion lift?', 'test01')
print(r.answer)
print('label:', r.label)
"
```

**What you should see:** a response that mentions SKU IDs like 11, 38, or 6 (the top performers in the data), ending with `[Data-grounded]`. If it says `[General inference]` that is also fine — it means the model answered but went slightly beyond the provided data. If you get an error, check your endpoint URL has no trailing slash and the key was copied correctly.

---

## Option B — AWS Bedrock

### Part 1 — you do this in a browser (manual steps)

**Step 1 — create an AWS account (if you don't have one)**

- Go to: https://aws.amazon.com → click "Create an AWS Account"
- You will need a credit card but the free tier covers more than enough for a demo

**Step 2 — request Llama access in Bedrock**

- Log into the AWS Console: https://console.aws.amazon.com
- In the search bar at the top type `Bedrock` and open it
- In the left sidebar click **"Model access"**
- Click **"Modify model access"**
- Scroll to find **"Llama 3.1 8B Instruct"** under the Meta section and tick it
- Click "Request model access" — approval is usually instant

**Step 3 — create an IAM user and get credentials**

- In the AWS Console search bar type `IAM` and open it
- Click "Users" → "Create user" → give it any name (e.g. `dashboard-ai`)
- On the permissions page: "Attach policies directly" → search and tick `AmazonBedrockFullAccess`
- Finish creating the user, then click the user → "Security credentials" tab
- Click "Create access key" → choose "Local code" → download the CSV
- Save your `Access Key ID` and `Secret Access Key` from the CSV

**Step 4 — check your region**

The Bedrock code is already set to `eu-west-2` (London). Llama 3.1 is available there. If you are in the US, `us-east-1` also works — set `AWS_REGION=us-east-1` in that case.

---

### Part 2 — no code changes needed

The Bedrock provider is already written and wired up. Skip straight to Part 3.

---

### Part 3 — test the real connection (you do this)

**Mac / Linux:**
```bash
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_REGION="eu-west-2"
export LLM_PROVIDER="bedrock"
python -c "
from ai.services.chat_service import answer_question
r = answer_question('Which SKUs have the highest promotion lift?', 'test01')
print(r.answer)
print('label:', r.label)
"
```

**Windows PowerShell:**
```powershell
$env:AWS_ACCESS_KEY_ID="your-access-key-id"
$env:AWS_SECRET_ACCESS_KEY="your-secret-access-key"
$env:AWS_REGION="eu-west-2"
$env:LLM_PROVIDER="bedrock"
python -c "
from ai.services.chat_service import answer_question
r = answer_question('Which SKUs have the highest promotion lift?', 'test01')
print(r.answer)
print('label:', r.label)
"
```

---

## Running the full dashboard with the real model

Once the smoke test above works, launch the dashboard the same way but with your
env vars set:

```bash
# Mac/Linux
export LLM_PROVIDER=azure   # or bedrock
python -m dashboard.app

# Windows PowerShell
$env:LLM_PROVIDER="azure"   # or "bedrock"
python -m dashboard.app
```

Navigate to the **"8 · AI Chat"** tab and ask something like:
*"Which SKUs should I prioritise for promotion next quarter?"*

---

## Troubleshooting

**"Module not found: azure.ai.inference"**
Run `pip install azure-ai-inference==1.0.0b3`

**"AZURE_INFERENCE_ENDPOINT and AZURE_INFERENCE_KEY must be set"**
You forgot to set the env vars before running. They must be set in the same
terminal session you launch the dashboard from.

**Response ends with [General inference] instead of [Data-grounded]**
This is normal for questions about forecasting or elasticity — those context
files don't exist yet (the ML pod hasn't written them). Promotion lift questions
should ground correctly since `ai_context_module7.json` is in the repo.

**Model says "I don't have data on this"**
Also normal for the same reason above. Not a bug.

**Azure 401 Unauthorized**
Your key was copied incorrectly or has a space at the start/end. Re-copy it
directly from the Azure portal.

**Bedrock "AccessDeniedException"**
The model access request hasn't been approved yet, or you are hitting a region
that doesn't have the model. Try switching to `AWS_REGION=us-east-1`.

---

## Important — never commit your credentials

Do not put your API key or AWS secret into any file in the repo. Always set them
as environment variables in your terminal. If you accidentally commit a key,
rotate it immediately in the Azure or AWS portal.
