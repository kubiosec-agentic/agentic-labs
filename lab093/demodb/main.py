#!/usr/bin/env python3
"""
AI Research Agent - Main Script
Automatically researches and stores latest AI developments
"""

import sys
import argparse
from datetime import datetime
from ai_researcher import AIResearcher

def main():
    parser = argparse.ArgumentParser(description='AI Research Agent')
    parser.add_argument('--research', action='store_true', help='Run research process')
    parser.add_argument('--show', type=int, default=10, help='Show recent results (default: 10)')
    parser.add_argument('--vendor', type=str, help='Filter by vendor')
    
    args = parser.parse_args()
    
    researcher = AIResearcher()
    
    if args.research:
        print("=" * 50)
        print("AI RESEARCH AGENT")
        print("=" * 50)
        print(f"Started at: {datetime.now()}")
        
        try:
            researcher.research_ai_news()
        except KeyboardInterrupt:
            print("\nResearch interrupted by user")
        except Exception as e:
            print(f"Research error: {e}")
            sys.exit(1)
    
    # Show recent results
    print(f"\nRecent AI Research Results (limit: {args.show}):")
    print("-" * 60)
    
    try:
        results = researcher.get_recent_research(args.show, args.vendor)
        
        if not results:
            if args.vendor:
                print(f"No results found for vendor '{args.vendor}'. Run with --research to gather data.")
            else:
                print("No results found. Run with --research to gather data.")
            return
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['title']}")
            print(f"   Vendor: {result['vendor']}")
            print(f"   Category: {result['category']}")
            print(f"   Date: {result['research_date']}")
            print(f"   URL: {result['url']}")
            if result['summary']:
                print(f"   Summary: {result['summary'][:100]}...")
            if result['tags']:
                print(f"   Tags: {', '.join(result['tags'])}")
            print("-" * 60)
            
    except Exception as e:
        print(f"Error retrieving results: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()