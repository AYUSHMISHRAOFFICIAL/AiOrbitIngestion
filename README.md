# AI Orbit Ecosystem Data Ingestion Pipeline

A production-grade, modular, Python-based bulk data ingestion pipeline designed to extract, clean, normalize, deduplicate, and output structured data for the AI Orbit platform. 

## Features

- **Multi-Source Ingestion**: Pulls entities from GitHub, Hugging Face, YouTube, and RSS feeds.
- **Robust Entity Resolution**: 5-level deterministic deduplication strategy merging identical real-world entities.
- **Evidence-based Relationships**: Extracts relationships with confidence scores based on concrete evidence.
- **Secure Architecture**: Implements strict SSRF protection, rejecting internal/private IP accesses, enforcing HTTPS limits, and validating redirects.
- **Stable ID Generation**: Uses deterministic UUIDv5 identifiers ensuring consistent entity identity across pipeline runs.

## Prerequisites

- Python 3.10+
- `pip` package manager

### API Credentials (Optional but Recommended)
To prevent rate limits and enable YouTube discovery, provide credentials via the `.env` file:
- `GITHUB_TOKEN`: Personal Access Token for GitHub API.
- `HF_TOKEN`: Hugging Face API token (optional).
- `YOUTUBE_API_KEY`: Google Cloud YouTube Data API v3 key (required for video entities).

## Installation

1. Clone or copy the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy the environment template:
   ```bash
   cp .env.example .env
   ```
4. Fill in `.env` with your API credentials.

## Usage

Run the pipeline using the orchestrator script:
```bash
python run.py
```

### Outputs
Data is written to `data/final/`:
- `entities.json`: The fully normalized and strictly validated AI ecosystem entities across the required taxonomy categories.
- `relationships.json`: The mapping of semantic relationships between entities (e.g. `develops_tool`, `develops_model`, `solves_task`, `integrates_with`, `runs_model`).

## Development and Testing

Run the test suite using:
```bash
python -m pytest -q
```

Tests cover HTTP retry behavior, API adapters, URL/name normalization, SSRF protection, entity resolution, classification taxonomy, relationship extraction, deterministic filtering, referential integrity, and pipeline validation.

## Architecture

* `src/sources/`: API Adapters and the secure HTTP client.
* `src/processing/`: Text cleaning, normalization, and classification modules.
* `src/resolution.py`: Deduplication and entity resolution.
* `src/relationships.py`: Semantic linkage of entities.
* `src/io.py`: File operations and strict boundary validation using Pydantic.
