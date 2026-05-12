# AI Invoice Analysis — Backend

Production-grade serverless backend for extracting structured data from invoice documents using AWS Textract.

---

## Architecture

```
React Frontend
      │
      ▼
API Gateway → API Lambda (FastAPI + Mangum)
                    │
              ┌─────┴──────┐
              ▼            ▼
    POST /generate-    GET /invoice(s)
    upload-url              │
              │          DynamoDB
              ▼
        S3 Presigned
            URL
              │
              ▼  (client PUTs file directly)
             S3
              │
              ▼  (S3 event notification)
             SQS
              │
              ▼
   Processing Lambda (handler.py)
       │
  ┌────┼────────────┐
  ▼    ▼            ▼
Textract  Parser  DynamoDB
          │
          ▼
       Summary
       Service
```

---

## Project Structure

```
backend/
├── api_lambda/
│   ├── main.py                  ← FastAPI app + handler = Mangum(app)
│   ├── routes/invoice_routes.py ← 3 routes, zero business logic
│   ├── services/
│   │   ├── invoice_service.py   ← orchestration
│   │   └── s3_service.py        ← presigned URL generation
│   ├── repositories/
│   │   └── invoice_repository.py ← DynamoDB reads + pagination
│   ├── models/invoice.py        ← Invoice dataclass
│   ├── schemas/invoice_schema.py ← Pydantic v2 validation
│   ├── utils/
│   │   ├── response_formatter.py
│   │   └── logger.py
│   ├── exceptions/custom_exceptions.py
│   └── config/settings.py
│
├── processing_lambda/
│   ├── handler.py               ← lambda_handler entry point
│   ├── services/
│   │   ├── textract_service.py
│   │   ├── dynamodb_service.py
│   │   ├── summary_service.py
│   │   └── queue_service.py
│   ├── parsers/invoice_parser.py ← Textract blocks → Invoice model
│   ├── models/invoice.py
│   ├── utils/logger.py
│   └── exceptions/custom_exceptions.py
│
├── shared/                      ← reserved for cross-lambda utilities
└── template.yaml                ← AWS SAM IaC
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/generate-upload-url` | Validate file + return S3 presigned PUT URL |
| `GET`  | `/invoice/{invoice_id}` | Fetch single processed invoice |
| `GET`  | `/invoices` | List all processed invoices |
| `GET`  | `/health` | Lambda liveness check |

### Response Envelope

All responses use a standardised envelope:

```json
{ "success": true, "message": "...", "data": {} }
{ "success": false, "message": "...", "error": "..." }
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `S3_BUCKET_NAME` | Invoice upload bucket name | — |
| `DYNAMODB_TABLE_NAME` | DynamoDB table name | — |
| `AWS_REGION` | AWS deployment region | `us-east-1` |
| `PRESIGNED_URL_EXPIRY` | Presigned URL TTL in seconds | `300` |
| `MAX_FILE_SIZE_BYTES` | Maximum upload size | `10485760` (10 MB) |

Create a `.env` file in `api_lambda/` for local development:

```env
S3_BUCKET_NAME=my-invoice-bucket
DYNAMODB_TABLE_NAME=InvoicesTable-dev
AWS_REGION=us-east-1
PRESIGNED_URL_EXPIRY=300
MAX_FILE_SIZE_BYTES=10485760
```

---

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run FastAPI locally (api_lambda)
uvicorn api_lambda.main:app --reload --port 8000

# API docs available at:
# http://localhost:8000/docs
```

---

## Deployment

### Prerequisites

- AWS CLI configured (`aws configure`)
- AWS SAM CLI installed (`brew install aws-sam-cli`)
- Python 3.12

### Deploy

```bash
cd backend/

# Build Lambda packages + layer
sam build

# Deploy to AWS (first time — guided)
sam deploy --guided

# Subsequent deploys
sam deploy --parameter-overrides Environment=prod
```

### Teardown

```bash
sam delete --stack-name ai-invoice-backend-dev
```

---

## DynamoDB Table Schema

| Attribute | Type | Key |
|-----------|------|-----|
| `invoice_id` | String | Partition Key |
| `vendor_name` | String | — |
| `invoice_date` | String | — |
| `due_date` | String | — |
| `currency` | String | — |
| `tax_amount` | String | — |
| `total_amount` | String | — |
| `line_items` | List | — |
| `extracted_json` | Map | — |
| `summary` | String | — |
| `s3_path` | String | — |
| `created_at` | String (ISO 8601) | — |

---

## Custom Exceptions

| Exception | Lambda | Trigger |
|-----------|--------|---------|
| `S3UploadException` | API | S3 presigned URL generation failure |
| `DynamoDBException` | Both | Any DynamoDB read/write failure |
| `InvoiceNotFoundException` | API | invoice_id not in DynamoDB |
| `TextractProcessingException` | Processing | Textract API failure |
| `InvoiceParsingException` | Processing | Empty/malformed Textract blocks |
| `QueueServiceException` | Processing | SQS delete/attribute failure |

---

## IAM Permissions (Least Privilege)

### API Lambda
- `s3:PutObject`, `s3:GetObject` — uploads prefix only
- `dynamodb:GetItem`, `dynamodb:Scan` — InvoicesTable only

### Processing Lambda
- `s3:GetObject` — uploads prefix only
- `textract:AnalyzeDocument` — any resource (required by Textract)
- `dynamodb:PutItem` — InvoicesTable only
- `sqs:ReceiveMessage`, `sqs:DeleteMessage`, `sqs:GetQueueAttributes`

---

## Coding Standards

- **No `print()` anywhere** — all output via `logging.getLogger(__name__)`
- **Every boto3 call wrapped** in `try/except ClientError` → custom exception
- **Pydantic v2** schemas validate all input before services are called
- **Full type hints** on every function signature
- **OOP layer separation**: Routes → Services → Repositories → AWS
