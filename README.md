# Active Personas - An Early Prototype

This is the Python implementation of the [Active Personas](https://active-personas.github.io/) framework - an innovative approach for persona-driven user experience evaluation using Large Language Models (LLMs).

## Overview

Active Personas enables automated UX evaluation by simulating realistic user feedback through AI-powered personas. This prototype implements the core framework components for conducting Nielsen's heuristic evaluations using multiple LLM providers, including GPT-5, Gemini 2.5 Pro, Llama 4 (Maverick), and Claude 4.

## Quick Start

### Installation

1. **Create and activate Python environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env-example .env
   ```
   
   Edit `.env` and configure these key parameters:
   ```env
   BASE_URL=https://openrouter.ai/api/v1
   OPENAI_API_KEY=your_api_key_here
   LOG_FILE=./logs/app.log
   LOG_LEVEL=INFO
   ```

### Basic Usage

Run Nielsen heuristic evaluations:

```bash
python run_nielsen_evaluation.py
```

## Configuration

### Workflow Settings

Configure which parts of the evaluation pipeline to run in `run_nielsen_evaluation.py`:

```python
# Enable/disable workflow steps
run_evaluations_enabled = True              # Execute new evaluations
perform_statistical_analysis_enabled = True # Perform statistical analysis
```

### Evaluation Parameters

```python
# LLM models to use for evaluation
llm_model_names = ['llama', 'claude', 'gemini', 'openai']

# Persona profiles to simulate
persona_names = ['claudio', 'ingrid']

# Number of evaluation iterations per persona-model combination
iterations = 10

# Interface images for evaluation
images = [
    "./data/img/skn_small/1-skn_home_screen_en.jpg",
    "./data/img/skn_small/2-skn_search_journey_screen_en.jpg",
    # Add more image paths...
]
```

### Output Structure

Results are saved with date-based organization:
```
result/
└── YYYYMMDD/              # Date-based directory
    ├── persona_model_nielsen_evaluation_results.csv
    └── stats/
        ├── analysis/
        └── merged_datasets.csv
```

## Key Features

- **Multi-LLM Support**: Evaluate with different AI models for comparative analysis
- **Persona-Based Evaluation**: Simulate diverse user perspectives and demographics
- **Nielsen Heuristics**: Automated usability evaluation based on established principles
- **Statistical Analysis**: Built-in Kruskal-Wallis tests for significance testing
- **Multi-Modal Input**: Support for text, image, and audio evaluation materials
- **Configurable Logging**: File-based logging with adjustable levels

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BASE_URL` | LLM API endpoint | `https://openrouter.ai/api/v1` |
| `OPENAI_API_KEY` | API key for LLM access | Required |
| `LOG_FILE` | Path to log file | `./logs/app.log` |
| `LOG_LEVEL` | Minimum log level | `INFO` |
| `PERSONA_DIR` | Directory containing persona files | `personas` |
| `PROMPT_DIR` | Directory containing prompt templates | `prompts` |
| `RESULT_DIR` | Base directory for results | `results` |

## Project Structure

```
early-prototype/
├── components/           # Core framework components
│   ├── active_persona.py    # AI persona implementation
│   ├── evaluator.py         # Base evaluation framework
│   ├── nielsen_evaluator.py # Nielsen heuristics evaluator
│   ├── llm_client.py        # LLM API client
│   ├── llm_factory.py       # LLM client factory
│   ├── data_analyzer.py     # Statistical analysis tools
│   └── logger.py            # Centralized logging
├── data/                 # Evaluation assets
│   └── img/              # Interface images
├── persona/            # Persona definition files
├── prompt/             # Evaluation prompt templates
├── result/             # Evaluation outputs
└── run_nielsen_evaluation.py  # Main execution script
```

## Contributing

This is an early prototype under active development. For issues, feature requests, or contributions, please visit the [Active Personas GitHub organization](https://github.com/active-personas-org).
