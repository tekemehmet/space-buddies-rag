# Space Buddies RAG

A Python-based RAG data preparation project for the **NASA Space Apps Challenge 2026**.

The project collects official NASA content for selected explorers, cleans the source text, converts it into smaller searchable chunks, and prepares the data for later use with **Azure AI Search**, **Azure OpenAI**, and other Azure AI services.

## Explorers

Current collectors support:

- Opportunity
- Spirit
- InSight
- Ingenuity
- Apollo Lunar Module
- Lunar Roving Vehicle

## Project Structure

```text
space-buddies-rag/
├── data/
│   ├── raw/
│   └── processed/
│
├── scripts/
│   ├── collector_common.py
│   ├── collect_opportunity.py
│   ├── collect_spirit.py
│   ├── collect_insight.py
│   ├── collect_ingenuity.py
│   ├── collect_lunar_module.py
│   ├── collect_lunar_rover.py
│   ├── create_chunks.py
│   └── inspect_chunks.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

Create and activate a Python virtual environment.

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Collect NASA Data

Run collectors from the project root.

Opportunity:

```bash
python scripts/collect_opportunity.py
```

Spirit:

```bash
python scripts/collect_spirit.py
```

InSight:

```bash
python scripts/collect_insight.py
```

Ingenuity:

```bash
python scripts/collect_ingenuity.py
```

Apollo Lunar Module:

```bash
python scripts/collect_lunar_module.py
```

Lunar Roving Vehicle:

```bash
python scripts/collect_lunar_rover.py
```

The collected source documents are saved under:

```text
data/raw/
```

## Create RAG Chunks

After collecting the source documents:

```bash
python scripts/create_chunks.py
```

The processed chunks are written to:

```text
data/processed/chunks.jsonl
```

Each chunk contains searchable content plus metadata such as:

- explorer
- mission
- topic
- NASA source title
- source URL
- document ID

## Inspect the Chunks

Review the generated chunks before uploading them to Azure:

```bash
python scripts/inspect_chunks.py
```

The script prints each chunk's:

- ID
- topic
- word count
- content preview

## Planned RAG Flow

```text
NASA Sources
    ↓
Raw JSON
    ↓
Semantic Chunks
    ↓
Embeddings
    ↓
Azure AI Search
    ↓
Relevant NASA Context
    ↓
Azure OpenAI
    ↓
Grounded Explorer Response
    ↓
NASA Citations
```

## Azure Integration

Planned services include:

- Azure AI Search
- Azure OpenAI
- Azure AI Foundry
- Azure Speech for Text-to-Speech
- Azure hosting for the backend and frontend

## Data Policy

Generated data under `data/raw/` and `data/processed/` is excluded from Git by default. The collection and processing scripts can regenerate these files from the original NASA sources.

## Goal

The goal of **Space Buddies** is to let students interact with NASA explorers through a grounded AI experience where each explorer tells its story using information retrieved from official NASA sources.
