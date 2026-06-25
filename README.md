# 🔍 ClaimLens

### Gemini-Powered Reimbursement Document Review

ClaimLens is a Gemini-powered reimbursement review prototype that transforms redacted PDFs and invoice images into schema-validated JSON, structured finance tables, deterministic risk checks, and downloadable review artifacts.

> Built for the **Build with Gemini** hackathon using Gemini multimodal document understanding, structured output, Pydantic validation, and transparent Python review rules.

---

## 🚀 Live Demo

[Open the Streamlit Demo](YOUR_STREAMLIT_URL)

## 🎥 YouTube Demo

[Watch the Demo Video](YOUR_YOUTUBE_URL)

---

## 📖 Project Overview

ClaimLens is an independent implementation created for the Build with Gemini hackathon. It is inspired by an earlier reimbursement workflow concept, but this Gemini edition has its own technical architecture and implementation.

This project does **not** use:

* Band agents
* Band SDK
* Band Remote Agents
* WebSocket orchestration
* Multi-agent collaboration frameworks

Instead, ClaimLens is built around a **Gemini multimodal document-processing pipeline** combined with deterministic Python review logic.

A finance reviewer can upload up to three redacted reimbursement documents. Gemini analyzes both visible text and document layout, classifies document types, extracts structured reimbursement records, and returns schema-constrained JSON.

Python then validates the response and performs calculations and rule-based checks that should not be delegated to a language model.

---

## 💡 Inspiration

Reimbursement evidence is often scattered across invoices, receipts, payment screenshots, bank statements, travel records, supporting documents, and even filenames.

Reviewers may need to compare:

* Document types
* Visible totals
* Dates
* Currencies
* Counterparties
* Invoice numbers
* Payment references
* Proof of payment
* Claimed reimbursement totals

Traditional OCR may extract isolated text while missing tables, labels, screenshots, and relationships created by visual layout.

ClaimLens demonstrates how Gemini multimodal understanding can reduce this manual friction while keeping the final review process transparent and human-controlled.

---

## 🧾 The Reimbursement Problem

Finance teams need to determine:

* What type of evidence each document contains
* Which amounts and currencies are visible
* Whether payment proof exists
* Whether multiple currencies appear in the same package
* Whether critical invoice fields are missing
* Whether a claimed total in the filename matches the extracted evidence
* Whether the package requires manual review

Manual review is slow and error-prone, especially when supporting evidence includes screenshots, tables, mixed currencies, or inconsistent document formats.

ClaimLens combines multimodal extraction with deterministic validation to make these issues easier to identify.

---

## ✨ What the Application Does

* Accepts PDF, PNG, JPG, and JPEG uploads
* Supports up to three files in one review
* Sends document content to Gemini for multimodal understanding
* Reads visible text, tables, labels, screenshots, and layout relationships
* Classifies reimbursement document types
* Extracts structured reimbursement records
* Validates Gemini output with Pydantic
* Runs deterministic Python review rules
* Displays metrics, records, warnings, and layout observations
* Provides expandable structured JSON
* Exports review records as CSV and JSON
* Handles missing API keys without presenting cached data as live output
* Clearly labels sample results as non-live Gemini responses

Supported document classifications include:

```text
invoice
receipt
bank_statement
payment_proof
wechat_transfer
travel_document
supporting_document
unknown
```

---

## 🤖 How ClaimLens Uses the Gemini API

The live processing path is implemented in `gemini_client.py` using the official Google Gen AI Python SDK.

| Component                    | Implementation                        |
| ---------------------------- | ------------------------------------- |
| SDK                          | `google-genai`                        |
| Default model                | `gemini-2.5-flash`                    |
| API key environment variable | `GEMINI_API_KEY`                      |
| Optional model override      | `GEMINI_MODEL`                        |
| Main API method              | `client.models.generate_content(...)` |
| Inline file input            | `types.Part.from_bytes(...)`          |
| Large-document path          | Gemini Files API                      |
| Response format              | `application/json`                    |
| Response schema              | `ReimbursementExtractionResult`       |

Example configuration:

```python
response = client.models.generate_content(
    model=model_name,
    contents=contents,
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=ReimbursementExtractionResult,
    ),
)
```

For inline document processing, files are converted into Gemini parts:

```python
types.Part.from_bytes(
    data=file_bytes,
    mime_type=mime_type,
)
```

Larger PDFs can be handled through:

```python
client.files.upload(...)
```

### Official Documentation

* [Google Gen AI SDK Libraries](https://ai.google.dev/gemini-api/docs/libraries)
* [Gemini Document Processing](https://ai.google.dev/gemini-api/docs/document-processing)
* [Gemini Structured Output](https://ai.google.dev/gemini-api/docs/structured-output)
* [Gemini Models](https://ai.google.dev/gemini-api/docs/models)

---

## 👁️ Why Multimodal Understanding Is Necessary

Reimbursement review depends on more than plain OCR text.

For example:

* A payment record may exist only as a screenshot
* A total may appear inside a table
* A currency symbol may appear in a column header
* A transaction status may be indicated by a visual label
* An invoice number may be positioned next to a specific field
* A filename may contain a claimed total that the document evidence does not support

Gemini can analyze text and visual layout together, making it suitable for messy financial documents where isolated OCR output is not enough.

---

## 🔄 Document-Processing Pipeline

```text
Upload files
     ↓
Validate type, count, and size
     ↓
Send document content to Gemini
     ↓
Analyze text and visual layout
     ↓
Classify document types
     ↓
Extract structured reimbursement records
     ↓
Return schema-constrained JSON
     ↓
Validate response with Pydantic
     ↓
Apply deterministic Python review rules
     ↓
Display findings and downloadable artifacts
```

Detailed workflow:

1. The user uploads redacted PDFs or images.
2. The application validates file count, MIME type, and file size.
3. Gemini analyzes document content and layout.
4. Gemini classifies each document or record.
5. Gemini extracts reimbursement-related fields.
6. Gemini returns JSON matching the Pydantic response schema.
7. Pydantic validates the response before it reaches the interface.
8. Python calculates totals and deterministic risk signals.
9. Streamlit displays metrics, tables, findings, JSON, and exports.

---

## 🧩 Structured Output and Pydantic Validation

The response schemas are defined in `schemas.py`.

### `ExtractedRecord`

Each extracted record can contain:

* Source filename
* Page or item reference
* Document type
* Invoice number
* Transaction or invoice date
* Amount
* Currency
* Seller or counterparty
* Payment reference
* Payment-proof status
* Layout summary
* Uncertain fields
* Record-level warnings

### `ReimbursementExtractionResult`

The top-level result can contain:

* Source files
* Document summary
* Extracted records
* Detected document types
* Detected currencies
* Filename claims
* Extracted totals
* Payment-proof status
* Layout observations
* Uncertain findings
* Warnings
* Recommended review action

If Gemini returns an invalid structure, ClaimLens does not silently continue or make a financial decision.

Instead, it displays a safe diagnostic message and asks the reviewer to retry or inspect the source documents.

---

## ⚖️ Deterministic Review Rules

Gemini is responsible for interpreting the documents. Python is responsible for calculations and explicit review rules.

Python checks include:

* Total amount by currency
* Extracted record count
* Invoice count
* Payment-proof count
* Missing critical fields
* Multiple-currency detection
* Filename-total comparison
* Claimed-total mismatch
* Cross-currency review flags
* Human-review recommendation

Example rules include:

* Multiple detected currencies require manual review
* Invoice evidence without visible payment proof creates a warning
* Filename totals are treated as claims, not approval evidence
* Missing amount or currency requires human review
* A mismatch between a filename claim and extracted totals requires rechecking
* Cross-currency amounts are not automatically combined
* Exchange-rate conversion is not performed without an explicit policy

This separation keeps mathematical checks reproducible and makes the review process easier to audit.

---

## 🧪 Example Workflow

1. Open the ClaimLens web application.

2. Upload a redacted reimbursement file, such as:

   ```text
   demo_case_02_mar30_mar31_total_1990_20_minimal_redacted.pdf
   ```

3. Click **Run Gemini Review**.

4. Confirm that the application displays:

   ```text
   LIVE GEMINI REVIEW
   ```

5. Inspect:

   * Document classifications
   * Extracted records
   * Amounts and currencies
   * Payment-proof status
   * Layout observations
   * Deterministic warnings
   * Recommended review action
   * Structured JSON

6. Download the resulting CSV or JSON artifact.

### Sample Mode

When no Gemini API key is configured, the application displays:

```text
GEMINI API KEY NOT CONFIGURED
```

The user may manually select:

```text
Load Redacted Sample Result
```

Sample mode is clearly labeled:

```text
SAMPLE / CACHED RESULT — NOT A LIVE GEMINI RESPONSE
```

ClaimLens does not present cached sample data as live Gemini output.

---

## 🖼️ Screenshots

Add public screenshots to the `assets/` directory after deployment:

```text
assets/screenshot-upload.png
assets/screenshot-live-review.png
assets/screenshot-records-table.png
assets/screenshot-json-export.png
```

Suggested README layout:

```markdown
### Upload Interface

![ClaimLens upload interface](assets/screenshot-upload.png)

### Live Gemini Review

![Live Gemini review](assets/screenshot-live-review.png)

### Extracted Records

![Structured records table](assets/screenshot-records-table.png)

### JSON and Export

![JSON and export interface](assets/screenshot-json-export.png)
```

---

## 🛠️ Technology Stack

* Python 3.11-compatible code
* Streamlit
* Google Gen AI Python SDK
* Gemini `gemini-2.5-flash`
* Pydantic
* Pandas
* python-dotenv
* Pillow
* Pytest

---

## 📁 Project Structure

```text
CLAIMLENS/
├── streamlit_app.py
├── gemini_client.py
├── schemas.py
├── review_rules.py
├── file_utils.py
├── requirements.txt
├── README.md
├── VIDEO_SCRIPT_EN.md
├── DEVPOST_SUBMISSION.md
├── .env.example
├── .gitignore
├── LICENSE
├── prompts/
│   └── document_extraction.md
├── sample_data/
│   ├── sample_result.json
│   ├── sample_records.csv
│   └── README.md
├── assets/
│   └── README.md
└── tests/
    ├── test_filename_parser.py
    ├── test_schemas.py
    └── test_review_rules.py
```

---

## 💻 Local Installation

### macOS or Linux

```bash
cd CLAIMLENS

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Windows PowerShell

```powershell
cd C:\path\to\CLAIMLENS

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
streamlit run streamlit_app.py
```

The application should then be available locally at:

```text
http://localhost:8501
```

---

## 🔑 Configure `GEMINI_API_KEY` Locally

Create a local `.env` file based on `.env.example`:

```env
GEMINI_API_KEY=replace_with_your_api_key
GEMINI_MODEL=gemini-2.5-flash
```

Do not commit the `.env` file.

It should remain excluded through `.gitignore`.

---

## ☁️ Streamlit Community Cloud Deployment

### When `CLAIMLENS` Is Its Own GitHub Repository

Use:

```text
Main file path: streamlit_app.py
```

### When `CLAIMLENS` Is Inside a Larger Repository

Use:

```text
Main file path: CLAIMLENS/streamlit_app.py
```

### Deployment Steps

1. Push the project to GitHub.
2. Open Streamlit Community Cloud.
3. Create a new application.
4. Select the GitHub repository and branch.
5. Enter the correct main file path.
6. Add the required Streamlit secrets.
7. Deploy the application.
8. Replace `YOUR_STREAMLIT_URL` in this README with the public application URL.

The dependencies are installed from:

```text
requirements.txt
```

---

## 🔐 Configure Streamlit Secrets

In the Streamlit Community Cloud application settings, add:

```toml
GEMINI_API_KEY = "your_api_key"
GEMINI_MODEL = "gemini-2.5-flash"
```

The public application interface should not ask visitors to enter an API key.

After changing a secret, restart or redeploy the application if necessary.

---

## 🛡️ Security and Privacy

* No Gemini API key is hardcoded
* Local `.env` files are excluded from Git
* Streamlit secret files are not committed
* The application does not intentionally retain uploaded documents
* Temporary local files used during processing are removed after use
* Cached sample results are clearly labeled as non-live data
* Error messages avoid exposing API credentials
* Public users are not asked to provide an API key

Documents sent to Gemini are processed through the configured Gemini API. Their handling is therefore also subject to the applicable Google API terms, data-use policies, and account configuration.

Do not upload private, confidential, or unredacted financial documents to a public demonstration deployment.

---

## ⚠️ Known Limitations

* ClaimLens is a review assistant, not an approval authority
* Extracted results still require human verification
* Filename totals are parsed only when an explicit pattern such as `total_1990_20` is present
* Currency inference is intentionally cautious
* Cross-currency values are not automatically combined
* Exchange-rate conversion is not performed
* Gemini output quality depends on document quality and visible evidence
* Heavy redaction may remove information needed for accurate extraction
* Poor image resolution may reduce extraction quality
* Live Gemini processing requires a valid API key
* Organization-specific reimbursement policies are not yet configurable

---

## 🗺️ Future Roadmap

* Add exchange-rate lookup with explicit policy controls
* Add configurable organization reimbursement policies
* Add reviewer annotations and approval notes
* Add batch comparison across reimbursement packages
* Add duplicate-invoice detection
* Add stronger pre-upload redaction checks
* Add export templates for finance teams
* Add reviewer decision history
* Add confidence indicators for uncertain fields
* Add support for more financial document categories

---

## 🏆 Build with Gemini Hackathon Statement

This Gemini implementation was created for the **Build with Gemini Devpost hackathon**.

It demonstrates a working Gemini API prototype for real-world multimodal financial document review using:

* Gemini `gemini-2.5-flash`
* Multimodal PDF and image understanding
* Structured JSON output
* Pydantic schema validation
* Deterministic Python finance checks
* A public Streamlit interface
* Downloadable review artifacts

The project is an independent implementation inspired by an earlier reimbursement workflow concept. It does not use Band agents, Band SDK, WebSocket orchestration, or a multi-agent framework.

---

## 📄 License

This project is licensed under the MIT License.

See [`LICENSE`](LICENSE) for details.

---

## ⚠️ Disclaimer

ClaimLens is a prototype for document review and decision support.

It does not provide accounting, tax, legal, compliance, or financial advice. Extracted information and automated warnings must be verified by a qualified human reviewer before any reimbursement or payment decision is made.
