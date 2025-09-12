# AI Research Agent

An intelligent agent that automatically researches the latest AI developments and stores them in a database.

## Features

- **Web Research**: Scrapes AI news from major sources (OpenAI, Google AI, Anthropic, etc.)
- **RSS Feed Monitoring**: Monitors RSS feeds from leading AI companies
- **AI Analysis**: Uses OpenAI GPT-4 to analyze and categorize content
- **Database Storage**: Stores results with metadata (date, vendor, tags, categories)
- **Deduplication**: Prevents storing duplicate content

## Setup

1. **Start Database**:
   ```bash
   docker-compose up -d
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

4. **Initialize Database**:
   The database schema is automatically created when Docker starts.

## Usage

**Run Research**:
```bash
python main.py --research
```

**View Results**:
```bash
python main.py --show 20
```

**Filter by Vendor**:
```bash
python main.py --show 10 --vendor "OpenAI"
```

## Database Access

- **Adminer UI**: http://localhost:8080
- **PostgreSQL**: localhost:5432 (admin/password123)
- **Redis**: localhost:6379

## Research Sources

- OpenAI Blog
- Google AI Blog  
- Anthropic Blog
- DeepMind Blog
- O'Reilly Radar
- Various AI RSS feeds

## Data Schema

```sql
CREATE TABLE ai_research (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    vendor VARCHAR(100),
    url VARCHAR(1000) UNIQUE,
    content_hash VARCHAR(64),
    research_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tags TEXT[],
    category VARCHAR(100),
    source_type VARCHAR(50) DEFAULT 'web'
);
```