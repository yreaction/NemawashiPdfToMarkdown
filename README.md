# Nemawashi PDF to Markdown Service

A microservice for converting PDF files to Markdown format using the pymupdf4llm library.

## Features

- Convert PDF files to well-formatted Markdown
- RESTful API using FastAPI
- Simple and efficient conversion process
- Security measures to prevent path traversal attacks

## Requirements

- Python 3.7+
- FastAPI
- pymupdf4llm
- uvicorn

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Running the server

```bash
python main.py
```

The server will start on http://localhost:8002 by default.

### API Endpoints

#### Convert PDF to Markdown

```
POST /extract_markdown
```

Request body:
```json
{
  "file_path": "/path/to/your/file.pdf"
}
```

Response:
```json
{
  "markdown_content": "# Converted Markdown content...",
  "file_path": "/path/to/your/file.pdf"
}
```

#### Health Check

```
GET /
```

Response:
```json
{
  "message": "Servicio PDF a Markdown está activo."
}
```

## Direct Conversion

You can also use the included `test_conversion.py` script to directly convert PDF files to Markdown without using the API.

```bash
python test_conversion.py
```

## License

MIT
