-- AI Research Database Schema

CREATE TABLE IF NOT EXISTS ai_research (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    vendor VARCHAR(100),
    url VARCHAR(1000) UNIQUE,
    content_hash VARCHAR(64),
    research_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tags TEXT[],
    category VARCHAR(100),
    source_type VARCHAR(50) DEFAULT 'web'
);

CREATE INDEX idx_ai_research_vendor ON ai_research(vendor);
CREATE INDEX idx_ai_research_date ON ai_research(research_date);
CREATE INDEX idx_ai_research_category ON ai_research(category);

-- Insert some sample categories for reference
INSERT INTO ai_research (title, summary, vendor, url, category, tags) VALUES 
('Sample Entry', 'This is a sample entry for testing', 'OpenAI', 'https://example.com', 'general', ARRAY['sample', 'test'])
ON CONFLICT (url) DO NOTHING;