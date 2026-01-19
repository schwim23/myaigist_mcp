# MyAIGist MCP Server

Local MCP server for Claude Desktop providing document intelligence and knowledge management. Process documents and answer questions with RAG - all running locally with zero infrastructure costs.

## Overview

**MyAIGist MCP** provides 10 powerful tools for document intelligence and knowledge management:

- **Document Processing**: PDF, DOCX, TXT, URLs, file attachments, and batch processing
- **Q&A System**: RAG-powered question answering
- **Knowledge Management**: Persistent vector storage with document tracking

## Features

✅ **Core document intelligence** - Process, summarize, and search documents
✅ **Claude-powered** - Uses Claude Sonnet 4.5 for summarization and Q&A
✅ **Local execution** - Runs in Claude Desktop
✅ **Persistent storage** - Single vector store across sessions
✅ **Multi-document RAG** - Unlimited documents (no 5-doc limit)
✅ **Zero infrastructure costs** - Replaces $200-400/month AWS deployment

## Installation

### Prerequisites

- Python 3.8+
- Anthropic API key (for Claude text generation)
- OpenAI API key (for embeddings)
- Claude Desktop installed

### Setup

1. **Install dependencies:**
   ```bash
   cd /Users/mikeschwimmer/myaigist_mcp
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add both API keys:
   # - ANTHROPIC_API_KEY (for Claude)
   # - OPENAI_API_KEY (for embeddings)
   ```

3. **Configure Claude Desktop:**

   Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "myaigist": {
         "command": "/Library/Frameworks/Python.framework/Versions/3.13/bin/python3",
         "args": ["/Users/mikeschwimmer/myaigist_mcp/server.py"]
       }
     }
   }
   ```

4. **Restart Claude Desktop**

   The MCP server will start automatically when you open Claude Desktop.

## Architecture

```
myaigist_mcp/               # MCP server (this project)
├── server.py               # Main MCP server with 10 tools
├── mcp_agents/             # All agent code (local, self-contained)
│   ├── document_processor.py  # PDF/DOCX/TXT extraction
│   ├── summarizer.py          # 3-level summarization (Claude)
│   ├── embeddings.py          # OpenAI embeddings
│   ├── url_crawler.py         # Web content extraction
│   ├── claude_client.py       # Anthropic client factory
│   ├── openai_client.py       # OpenAI client factory
│   ├── qa_agent.py            # Q&A with RAG (Claude)
│   └── vector_store.py        # Vector storage
└── data/                   # Persistent vector storage
    └── vector_store.pkl    # Created at runtime
```

**Architecture Notes:**
- All agents are self-contained in `mcp_agents/`
- No external dependencies on other projects
- Single-user design (no session/user isolation)
- Persistent vector storage with unlimited documents
- **Claude Sonnet 4.5** for text generation (summarization, Q&A)
- **OpenAI** for embeddings (RAG)

## Available Tools (10 Total)

### Content Processing (5 tools)

#### 1. `process_document`
Process a document from LOCAL FILE PATH (PDF, DOCX, TXT) and add to knowledge base.

**Parameters:**
- `file_path` (string, required): LOCAL filesystem path (e.g., /Users/mike/file.pdf)
- `title` (string, optional): Document title (defaults to filename)
- `summary_level` (string, optional): `quick`, `standard`, or `detailed`

**Example:**
```
"Process /Users/mike/contract.pdf as a detailed summary"
```

#### 2. `process_uploaded_document`
Process a document attached to Claude Desktop (recommended for file uploads).

**Parameters:**
- `content` (string, required): Text content extracted by Claude
- `filename` (string, required): Original filename
- `summary_level` (string, optional): `quick`, `standard`, or `detailed`

**Example:**
```
[Attach PDF file]
"Process this document with MyAIGist"
```

#### 3. `process_text`
Process raw text and add to knowledge base.

**Example:**
```
"Process this text: [paste long article]"
```

#### 4. `process_url`
Crawl web URL, extract content, and add to knowledge base.

**Example:**
```
"Process https://example.com/article"
```

#### 5. `process_batch`
Process multiple files and generate unified summary.

**Example:**
```
"Process all files in /Users/mike/research/ and give me a unified summary"
```

### Q&A System (1 tool)

#### 6. `ask_question`
Ask questions about stored documents using RAG.

**Example:**
```
"What are the main findings in the research papers?"
```

### Document Management (3 tools)

#### 7. `list_documents`
List all documents in knowledge base with metadata.

**Example:**
```
"Show me all my documents"
```

#### 8. `delete_document`
Delete specific document by ID.

**Example:**
```
"Delete document abc123xyz"
```

#### 9. `clear_all_documents`
Clear entire knowledge base.

**Example:**
```
"Clear all my documents"
```

### Utility Tools (1 tool)

#### 10. `get_status`
Get system status and knowledge base statistics.

**Example:**
```
"What's my system status?"
```

## Common Workflows

### File Upload (Recommended)
```
User: [Attaches PDF to Claude Desktop]
User: "Process this document with MyAIGist"
Claude: ✅ Processed with summary

User: "What are the key points?"
Claude: "The key points are..."
```

### Single Document Q&A
```
User: "Process /Users/mike/contract.pdf"
Claude: ✅ Processed with summary

User: "What are the payment terms?"
Claude: "The payment terms are net 30..."
```

### Multi-Document Research
```
User: "Process these 3 research papers: paper1.pdf, paper2.pdf, paper3.pdf"
Claude: ✅ Processed all 3 with unified summary

User: "What are the common findings across all papers?"
Claude: "The common findings are..."
```

## Configuration

### Environment Variables (.env)

```bash
# Anthropic API Key (required - for Claude text generation)
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929

# OpenAI API Key (required - for embeddings)
OPENAI_API_KEY=sk-your-key-here
OPENAI_EMBED_MODEL=text-embedding-3-large
```

### Model Selection

**Current Configuration:**
- **Claude Sonnet 4.5** (`claude-sonnet-4-5-20250929`) - Summarization and Q&A
- **text-embedding-3-large** - Higher accuracy for RAG vector search

**Why Two API Keys?**
- **Anthropic Claude**: Text generation (summarization, Q&A) - excellent quality
- **OpenAI**: Embeddings (Claude doesn't provide embeddings)

### Storage

**Vector Store:**
- Path: `data/vector_store.pkl`
- Format: Pickle with numpy arrays
- Persistence: Survives server restarts
- Capacity: Unlimited documents

## Cost Savings

**Before (AWS/Flask):** $200-400/month
- ECS Fargate compute
- Load balancer
- CloudWatch
- Data transfer

**After (MCP/Local):** $0/month infrastructure
- Runs locally on your machine
- Only API costs (usage-based)

**API Costs** (estimated monthly):
- **Claude Sonnet 4.5**: $3/$15 per 1M tokens (input/output)
- **OpenAI Embeddings**: $0.13 per 1M tokens

**Typical Usage:**
- 100 documents processed: ~$5-10
- 500 questions answered: ~$2-5
- **Total: ~$10-15/month** (vs $200-400 AWS)

## Troubleshooting

### Server won't start
```bash
# Check if Python can find dependencies
python3 -c "import mcp; print('✅ MCP installed')"

# Check syntax
python3 -m py_compile server.py

# Check logs
tail -f ~/Library/Logs/Claude/mcp-server-myaigist.log
```

### Import errors
```bash
# Test agent imports
cd /Users/mikeschwimmer/myaigist_mcp
python3 -c "from mcp_agents.summarizer import Summarizer; print('✅ Imports work')"
python3 -c "from mcp_agents.qa_agent import QAAgent; print('✅ QAAgent works')"
```

### API Key errors
```bash
# Check environment variables are set
python3 -c "import os; print('Anthropic:', bool(os.getenv('ANTHROPIC_API_KEY'))); print('OpenAI:', bool(os.getenv('OPENAI_API_KEY')))"
```

### Empty knowledge base after restart
- Check `data/vector_store.pkl` exists
- Verify file permissions (readable/writable)
- Check for errors in server logs

### File upload not working
- Use `process_uploaded_document` for Claude Desktop attachments
- Use `process_document` for local filesystem paths
- See tool descriptions for guidance

## Development

### Running Tests
```bash
# Test agent imports
python3 -c "from mcp_agents.qa_agent import QAAgent; qa = QAAgent(); print('✅ QAAgent works')"

# Test document processing
cd /Users/mikeschwimmer/myaigist_mcp
python3 -c "from mcp_agents.document_processor import DocumentProcessor; dp = DocumentProcessor(); print('✅ DocumentProcessor works')"
```

### Debugging
```bash
# Check server logs
tail -f ~/Library/Logs/Claude/mcp-server-myaigist.log

# Run server manually to see output
python3 /Users/mikeschwimmer/myaigist_mcp/server.py
```

## Project Structure

```
myaigist_mcp/
├── server.py              # Main MCP server (10 tools)
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
├── .env.example          # Template
├── README.md             # This file
├── mcp_agents/           # MCP-adapted agents
│   ├── __init__.py
│   ├── claude_client.py   # Anthropic client factory
│   ├── summarizer.py      # Modified: uses Claude
│   ├── qa_agent.py        # Modified: uses Claude, single-user
│   ├── vector_store.py    # Modified: no user filtering
│   ├── document_processor.py
│   ├── embeddings.py
│   ├── url_crawler.py
│   └── openai_client.py
└── data/                 # Persistent storage
    └── vector_store.pkl  # Vector embeddings and metadata
```

## Recent Changes

**2026-01-19:** Removed audio/video processing features
- Removed `process_media`, `process_uploaded_media`, and `ask_question_voice` tools
- Removed Whisper transcription and media file support
- Focused purely on document intelligence (text-based content)
- Simplified from 13 to 10 tools
- Removed audio/video dependencies and temporary file handling

**2026-01-19:** Updated to Claude Sonnet 4.5
- Migrated from OpenAI to Anthropic Claude for text generation
- Claude Sonnet 4.5 for summarization and Q&A (better quality)
- OpenAI still used for embeddings (Claude doesn't provide)
- Added `process_uploaded_document` tool for Claude Desktop file attachments
- Now requires both ANTHROPIC_API_KEY and OPENAI_API_KEY

## License

Same as original myaigist project.

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review MCP logs: `~/Library/Logs/Claude/mcp-server-myaigist.log`
3. Verify environment variables in `.env`
4. Test agent imports individually

---

**Last Updated:** 2026-01-19
**Project Status:** ✅ Complete - 10 core tools implemented and tested
**Models:** Claude Sonnet 4.5 (text) + OpenAI (embeddings)
**Cost Savings:** $200-400/month → ~$10-15/month
**Focus:** Document intelligence (text-based content only)
