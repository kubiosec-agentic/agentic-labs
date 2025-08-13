![LangChain](https://img.shields.io/badge/LangChain-lightgrey) ![OpenAI](https://img.shields.io/badge/OpenAI-lightblue) ![Google](https://img.shields.io/badge/Google-orange) ![Tools](https://img.shields.io/badge/Tools-purple) ![Weather](https://img.shields.io/badge/Weather-blue) ![Security](https://img.shields.io/badge/Security-red)

# LAB990 Addendum: Advanced LangChain Examples
## Introduction
This directory contains advanced LangChain examples that demonstrate practical, real-world applications. These examples extend beyond basic functionality to show integration with external APIs, multi-provider LLM swapping, and specialized use cases like security analysis.

## Set up your environment
```
export OPENAI_API_KEY="xxxxxxxxx"
```
For multi-provider examples, also set:
```
export GOOGLE_API_KEY="xxxxxxxxx"
```
Install dependencies:
```
pip install -r requirements.txt
```

## Lab instructions

#### Example 1: Real Weather Forecast with LangChain Tools
This example demonstrates a production-ready weather application using LangChain tools integrated with the Open-Meteo API. It provides real weather data including current conditions and forecasts with proper error handling and caching.

Features:
- Real-time weather data from Open-Meteo API
- Location geocoding using Nominatim
- Request caching and retry logic
- Detailed weather reports with hourly forecasts

```
python3 weather_forecast.py
```

#### Example 2: Multi-Provider LLM Swapping
This script shows how to easily swap between different LLM providers (OpenAI GPT and Google Gemini) using a simple configuration switch. Perfect for comparing outputs or building provider-agnostic applications.

Features:
- Switch between OpenAI GPT-3.5 and Google Gemini
- Terraform code generation example
- Environment variable configuration
- Error handling for missing API keys

```
python3 easy_swap.py
```

#### Example 3: Shell Script Security Analysis
An advanced security analysis tool that uses LangChain to perform comprehensive security reviews of shell scripts. It loads scripts from a directory and analyzes them for common security vulnerabilities.

Features:
- Recursive shell script discovery
- Security-focused prompt engineering
- Detailed vulnerability reporting with severity levels
- Best practices recommendations

First, create a test directory with shell scripts to analyze:
```
mkdir test_repo
# Add some .sh files to test_repo/ directory
```

Then run the security analysis:
```
python3 file_security_review.py
```

## Dependencies
The examples require the following packages (see `requirements.txt`):
- `langchain-openai` - OpenAI integration
- `langchain-core` - Core LangChain functionality
- `pydantic` - Data validation
- `openmeteo-requests` - Weather API client
- `pandas` - Data manipulation
- `requests-cache` - API response caching
- `retry-requests` - Request retry logic
- `geopy` - Geocoding services
- `numpy` - Numerical operations

## Notes
- The weather example uses the free Open-Meteo API (no API key required)
- The multi-provider example requires both OpenAI and Google API keys
- The security analysis tool is designed for educational purposes and defensive security analysis only

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)