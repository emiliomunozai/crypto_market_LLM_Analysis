# LLMAgent: AI Financial Analyst

## Overview
LLMAgent is an advanced AI-powered financial analysis tool that provides investment recommendations based on news and price data. The agent leverages multiple memory systems to build knowledge over time and improve decision-making.

## Features
- **Memory Systems**:
  - Sensory Memory: Stores recent market conditions (news and price data).
  - Short-Term Memory: Tracks recent trends and statistical features.
  - Procedural Memory: Holds analysis methods and strategies.
  - Long-Term Memory: Retains historical facts about market behavior.
  - Autobiographical Memory: Stores past decisions and outcomes.
  - Working Memory: Keeps current analytical thoughts.
  - Prospective Memory: Remembers key considerations for future decisions.
- **Decision-Making**:
  - Analyzes market data and trends.
  - Provides clear investment recommendations: `Long` or `Short` (No `Hold`).
  - Assigns confidence scores to recommendations.
  - Learns from past decisions through feedback processing.
- **Persistence**:
  - Stores and loads memory from disk to ensure continuity.

## Installation
### Prerequisites
- Python 3.8+
- Required dependencies listed in `requirements.txt`

### Setup
1. Clone this repository:
   ```sh
   git clone 
   cd llmagent
   ```
2. Create a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage
### Initialize the Agent
```python
from src.models.agent import LLMAgent

agent = LLMAgent(api_key="your_api_key", azure_endpoint="your_endpoint")
```

### Make a Recommendation
```python
decision = agent.make_recommendation("What should I do with my Tesla stock?")
print(decision.recommendation, decision.confidence, decision.reasoning)
```

### Update with Market Data
```python
agent.update_with_news(news_items)  # List of NewsItem objects
agent.update_with_prices(price_data)  # List of PriceData objects
```

### Process Feedback
```python
agent.process_feedback(decision_id="12345", outcome="profit", reward=0.8)
```

### Save and Load Memory
```python
agent.save_memory()  # Persist memory
agent.load_memory()  # Restore from disk
```

## Logging
Enable logging for better debugging:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

## Contact
For issues and feature requests, please open an issue in the repository.

