# PRD.md

# AI Invoice Analysis System

## Project Overview

AI-powered invoice analysis web application built using:

- React Frontend
- Python FastAPI Backend
- AWS Serverless Architecture

The system allows users to upload invoice documents and automatically extract structured invoice data using AWS Textract.

Extracted data will be displayed in:
- Table format
- JSON format
- Summary format

The architecture is fully serverless and event-driven using AWS Lambda.

---

# Objectives

## Primary Goals

- Upload invoices securely with file type and size validation
- Automatically extract invoice data using AWS Textract
- Store structured invoice information in DynamoDB
- Display extracted invoice details on frontend
- Use scalable AWS serverless architecture
- Maintain clean OOP backend structure
- Follow PEP8 coding standards
- Implement proper logging via CloudWatch (no print statements)
- Handle all AWS exceptions using custom exception classes
- Return standardised API response envelopes for all endpoints

---

# Tech Stack

## Frontend

| Technology | Purpose |
|---|---|
| React.js | UI |
| Axios | API Calls |
| Tailwind CSS | Styling |

---

## Backend

| Technology | Purpose |
|---|---|
| FastAPI | API Framework |
| Python 3.12 | Backend Runtime |
| Mangum | Lambda ASGI Adapter |
| Boto3 | AWS SDK |
| Pydantic | Request/Response Validation |

> **Note:** `main.py` must export `handler = Mangum(app)` as the Lambda entrypoint. Without this, API Gateway cannot invoke the FastAPI app.

---

## AWS Services

| Service | Purpose |
|---|---|
| AWS S3 | Invoice Storage (private bucket, HTTPS only) |
| AWS Lambda | Serverless Compute (API Lambda + Processing Lambda) |
| AWS Textract | OCR + Invoice Extraction |
| AWS DynamoDB | Structured Data Storage |
| AWS API Gateway | API Exposure |
| AWS SQS | Queue-based Async Processing |
| AWS CloudWatch | Logging & Monitoring (mandatory) |
| AWS IAM | Permissions & Security (least privilege) |
| AWS Rekognition | Optional Image Validation |

---

# System Architecture

```txt
React Frontend
        │
        ▼
   [File type + size validation in schema]
        │
        ▼
API Gateway
        │
        ▼
FastAPI Lambda  (Mangum adapter → handler = Mangum(app))
        │
        ▼
POST /generate-upload-url
        │
        ▼
Generate PreSigned URL (expires in 300s)
        │
        ▼
Frontend Upload → S3 (direct, no backend streaming)
        │
        ▼
S3 Event Notification
        │
        ▼
SQS Queue (buffers spikes, enables retries)
        │
        ▼
Processing Lambda → handler.py (lambda_handler)
        │
   ┌────┼──────────────┐
   ▼    ▼              ▼
Textract  DynamoDB  CloudWatch
   │
   ▼
invoice_parser.py  (hardest part — OCR block → structured dict)
   │
   ▼
summary_service.py  (generates human-readable summary string)
   │
   ▼
dynamodb_service.py  (table.put_item)
        │
        ▼
Frontend Fetch APIs (GET /invoice/{id} · GET /invoices)
```

---

# Functional Requirements

## 1. Invoice Upload

### Description

Users can upload:
- PDF
- PNG
- JPG
- JPEG

### Flow

1. Frontend sends file metadata to backend
2. Backend validates file type and file size before issuing URL
3. Backend generates S3 pre-signed URL (expires 300s)
4. Frontend uploads invoice directly to S3 via `axios.put(uploadUrl, file)`

### Acceptance Criteria

- Upload succeeds for valid file types
- Invalid file types rejected with `400` error response
- File size validation implemented (reject oversized files)
- Upload handled without backend file streaming
- Validation runs in Pydantic schema before service is called

---

## 2. Invoice Processing

### Trigger

S3 upload event triggers processing pipeline.

### Processing Steps

1. S3 fires event notification to SQS
2. SQS triggers Processing Lambda
3. `handler.py` reads `bucket_name` and `file_key` from event
4. `textract_service.py` calls `analyze_document()` with `TABLES` and `FORMS`
5. `invoice_parser.py` parses raw Textract JSON into structured dict
6. `summary_service.py` generates human-readable invoice summary string
7. `dynamodb_service.py` stores result via `table.put_item()`
8. CloudWatch logs all steps at appropriate levels

### Exception Handling Per Step

Every AWS call must be wrapped in `try-except ClientError` and raise the appropriate custom exception. See Exception Handling section.

---

## 3. Invoice Data Extraction

### Fields To Extract

| Field |
|---|
| Invoice Number |
| Vendor Name |
| Invoice Date |
| Due Date |
| Currency |
| Tax Amount |
| Total Amount |
| Line Items |
| Quantity |
| Unit Price |

---

## 4. Invoice Summary

### Responsibility

`summary_service.py` — a dedicated service method, not part of the parser.

### Example Output

```txt
Invoice from ABC Pvt Ltd dated 12 May 2026.
Total amount ₹12,999.
Contains 3 line items.
```

---

## 5. Invoice Display

Frontend must display:

### Table View

Structured invoice items table.

### JSON View

Raw extracted JSON.

### Summary View

Human-readable invoice summary string.

---

## 6. Invoice History

Users can:
- View all processed invoices via `GET /invoices`
- Re-open individual invoice results via `GET /invoice/{invoice_id}`

---

# Non-Functional Requirements

| Requirement | Description |
|---|---|
| Scalability | Serverless scaling via Lambda + SQS |
| Security | IAM least privilege; no AdministratorAccess |
| Availability | High availability via AWS managed services |
| Maintainability | Modular OOP architecture, clean layer separation |
| Logging | Centralised CloudWatch logging — no print() |
| Performance | Async processing via SQS + Processing Lambda |
| Reliability | Queue-based architecture with retry support |

---

# Backend Engineering Standards

## Code Standards

Backend must follow:

- PEP8
- SOLID principles
- DRY principles
- OOP architecture
- Type hints on all functions
- Separation of concerns
- Clean code standards

---

# OOP Architecture

| Layer | File(s) | Responsibility |
|---|---|---|
| Routes | `routes/invoice_routes.py` | Receive + validate requests, call services — NO business logic |
| Services | `services/invoice_service.py`, `s3_service.py`, `textract_service.py`, `dynamodb_service.py`, `summary_service.py`, `queue_service.py` | Business logic, all boto3 calls, AWS orchestration |
| Repositories | `repositories/invoice_repository.py` | Database read/write only — abstracts DynamoDB |
| Models | `models/` | Internal data structures |
| Schemas | `schemas/` | Pydantic request/response validation (file type + size validation lives here) |
| Utilities | `utils/response_formatter.py`, `utils/logger.py` | Shared response envelope, logger setup |
| Exceptions | `exceptions/` | Custom exception classes |
| Config | `config/` | Environment variables, settings |

---

# Exception Handling

All external AWS operations must use proper `try-except` blocks.

## Example

```python
try:
    response = textract.analyze_document(...)
except ClientError as error:
    logger.error(str(error))
    raise TextractProcessingException(
        "Textract processing failed"
    ) from error
```

---

# Custom Exceptions

```python
class S3UploadException(Exception):
    pass


class TextractProcessingException(Exception):
    pass


class DynamoDBException(Exception):
    pass
```

---

# Logging Standards

Use Python `logging` module only.

## Log Levels

- `INFO` — successful operations, processing milestones
- `WARNING` — recoverable issues
- `ERROR` — caught exceptions
- `CRITICAL` — unrecoverable failures

## Requirements

- CloudWatch integration mandatory
- `logger = logging.getLogger(__name__)` in every service file
- **No `print()` statements anywhere in the codebase**

---

# API Standards

## Response Formatter Utility

All routes must use a shared `utils/response_formatter.py` to return a consistent envelope:

### Success Response

```json
{
  "success": true,
  "message": "Invoice processed successfully",
  "data": {}
}
```

### Error Response

```json
{
  "success": false,
  "message": "Invoice processing failed",
  "error": "Textract timeout"
}
```

---

# API Design

## 1. Generate Upload URL

### Endpoint

```http
POST /generate-upload-url
```

### Validation (runs before service)

- File extension must be one of: `.pdf`, `.png`, `.jpg`, `.jpeg`
- File size must be within configured limit

### Response

```json
{
  "success": true,
  "message": "Upload URL generated",
  "data": {
    "upload_url": "signed-url",
    "file_key": "uploads/invoice.pdf"
  }
}
```

---

## 2. Get Invoice Details

### Endpoint

```http
GET /invoice/{invoice_id}
```

### Response

```json
{
  "success": true,
  "message": "Invoice fetched",
  "data": {
    "invoice_id": "INV-101",
    "summary": "Invoice from ABC Pvt Ltd...",
    "items": [],
    "json": {}
  }
}
```

---

## 3. Get All Invoices

### Endpoint

```http
GET /invoices
```

### Response

```json
{
  "success": true,
  "message": "Invoices fetched",
  "data": {
    "invoices": []
  }
}
```

---

# Database Design

## DynamoDB Table

```txt
InvoicesTable
```

## Primary Key

```txt
invoice_id (String)
```

## Attributes

| Attribute | Type | Description |
|---|---|---|
| invoice_id | String | Unique invoice identifier |
| vendor_name | String | Extracted vendor name |
| invoice_date | String | Invoice date |
| due_date | String | Payment due date |
| currency | String | Currency code |
| tax_amount | Number | Extracted tax amount |
| total_amount | Number | Extracted total amount |
| extracted_json | Map | Full Textract-parsed data |
| summary | String | Human-readable summary string |
| s3_path | String | S3 key of original file |
| created_at | String | ISO timestamp of processing |

---

# Recommended Project Structure

```txt
project/
│
├── frontend/
│
├── backend/
│   │
│   ├── api_lambda/
│   │   ├── main.py                  ← handler = Mangum(app) here
│   │   ├── routes/
│   │   │   └── invoice_routes.py
│   │   ├── services/
│   │   │   ├── invoice_service.py
│   │   │   └── s3_service.py
│   │   ├── repositories/
│   │   │   └── invoice_repository.py
│   │   ├── models/
│   │   ├── schemas/                 ← file type + size validation here
│   │   ├── utils/
│   │   │   ├── response_formatter.py  ← shared response envelope
│   │   │   └── logger.py
│   │   ├── exceptions/
│   │   │   └── custom_exceptions.py
│   │   └── config/
│   │
│   ├── processing_lambda/
│   │   ├── handler.py               ← lambda_handler entry point
│   │   ├── services/
│   │   │   ├── textract_service.py
│   │   │   ├── dynamodb_service.py
│   │   │   ├── summary_service.py   ← NEW: separate from parser
│   │   │   └── queue_service.py
│   │   ├── parsers/
│   │   │   └── invoice_parser.py    ← hardest part: Textract JSON → dict
│   │   ├── models/
│   │   ├── utils/
│   │   │   └── logger.py
│   │   └── exceptions/
│   │       └── custom_exceptions.py
│   │
│   └── shared/
│
├── template.yaml                    ← AWS SAM or Terraform IaC
├── requirements.txt
└── README.md
```

---

# Security Requirements

## IAM

- Least privilege permissions only
- No `AdministratorAccess`

## S3 Security

- Private bucket
- Block public access
- HTTPS only
- Presigned URL expiry: 300 seconds

## API Security

- Validate file types in Pydantic schema
- Validate file sizes in Pydantic schema
- Secure environment variables via Lambda env config

---

# Monitoring Requirements

Use CloudWatch for:

- Lambda invocation logs (INFO level per step)
- API failures (ERROR level)
- Timeout tracking (WARNING level)
- Processing metrics
- Error monitoring with full stack traces

---

# Performance Requirements

| Requirement | Target |
|---|---|
| Upload Time | < 5 sec |
| Extraction Time | < 15 sec |
| API Response | < 1 sec |
| Concurrent Users | 1000+ |

---

# Deployment Strategy

## Infrastructure as Code

Use:
- AWS SAM (`template.yaml`)
OR
- Terraform

Avoid:
- Manual AWS Console deployments

## Deployment Flow

```txt
GitHub Push
      │
      ▼
GitHub Actions
      │
      ▼
AWS SAM Build
      │
      ▼
AWS SAM Deploy
      │
      ▼
Lambda + API Gateway + S3 Deployment
```

---

# Future Enhancements

| Feature | AWS Service |
|---|---|
| Authentication | AWS Cognito |
| AI Summary Generation | AWS Bedrock |
| Notifications | SNS |
| Workflow Orchestration | Step Functions |
| Analytics | Athena |

---

# Success Criteria

Project is considered complete when:

- Invoice uploads successfully with file type and size validation
- Textract extracts invoice data accurately
- Data displayed in table, JSON, and summary formats
- CloudWatch logs operational — no `print()` statements in codebase
- All AWS boto3 calls wrapped in `try-except` with custom exceptions
- All API responses use the standardised `{ success, message, data }` envelope
- `GET /invoices` history endpoint functional
- `handler = Mangum(app)` correctly wired in `main.py`
- `summary_service.py` generates human-readable summaries as a separate step
- Backend follows OOP, PEP8, SOLID, and clean architecture
- Entire system deployed serverlessly using Lambda via SAM or Terraform