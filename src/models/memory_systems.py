from datetime import datetime
from typing import List, Dict, Optional
from .data_structures import NewsItem, PriceData, Fact, Decision, Consideration, Thought

class SensoryMemory:
    """
    Stores the most recent inputs (news and price data).
    Very short-term storage that captures current market conditions.
    """
    def __init__(self, max_size: int = 5):
        self.news_items: List[NewsItem] = []
        self.price_data: List[PriceData] = []
        self.max_size = max_size
    
    def add_news(self, news_item: NewsItem):
        self.news_items.append(news_item)
        if len(self.news_items) > self.max_size:
            self.news_items.pop(0)  # Remove oldest item
    
    def add_price(self, price_item: PriceData):
        self.price_data.append(price_item)
        if len(self.price_data) > self.max_size:
            self.price_data.pop(0)  # Remove oldest item
    
    def get_formatted(self) -> str:
        """Get formatted representation for prompt construction."""
        output = "## SENSORY MEMORY (CURRENT MARKET CONDITIONS)\n"
        
        # Format news items
        output += "\n### Latest News:\n"
        for item in self.news_items:
            output += f"- {item.date.strftime('%Y-%m-%d %H:%M')}: {item.text}\n"
        
        # Format price data
        output += "\n### Latest Prices:\n"
        for item in self.price_data:
            output += f"- {item.date.strftime('%Y-%m-%d %H:%M')}: {item.asset} at ${item.price:.2f}"
            if item.volume:
                output += f", Volume: {item.volume:.2f}"
            output += "\n"
        
        return output

class ShortTermMemory:
    """
    Stores recent historical data (news and prices with features).
    Maintains a rolling window of recent market history.
    """
    def __init__(self, max_news: int = 15, max_prices: int = 30):
        self.news_items: List[NewsItem] = []
        self.price_data: List[PriceData] = []
        self.max_news = max_news
        self.max_prices = max_prices
    
    def add_news(self, news_item: NewsItem):
        self.news_items.append(news_item)
        if len(self.news_items) > self.max_news:
            self.news_items.pop(0)  # Remove oldest item
    
    def add_price(self, price_item: PriceData):
        self.price_data.append(price_item)
        if len(self.price_data) > self.max_prices:
            self.price_data.pop(0)  # Remove oldest item
    
    def get_formatted(self) -> str:
        """Get formatted representation for prompt construction."""
        output = "## SHORT-TERM MEMORY (RECENT MARKET HISTORY)\n"
        
        # Add price statistics if available
        if self.price_data:
            latest_price_data = self.price_data[-1]
            output += "\n### Price Statistics:\n"
            if latest_price_data.close_7 is not None:
                output += f"- 7-day average: ${latest_price_data.close_7:.2f}\n"
            if latest_price_data.close_30 is not None:
                output += f"- 30-day average: ${latest_price_data.close_30:.2f}\n"
            if latest_price_data.close_90 is not None:
                output += f"- 90-day average: ${latest_price_data.close_90:.2f}\n"
        
        # Format news summary (limit to 5 most recent for prompt)
        output += "\n### Recent News Summary:\n"
        for item in self.news_items[-5:]:
            output += f"- {item.date.strftime('%Y-%m-%d %H:%M')}: {item.text}\n"
            
        return output

class ProceduralMemory:
    """
    Stores methods and procedures for analyzing market data.
    Contains guidance on how to analyze information.
    """
    def __init__(self):
        self.procedures = [
            "Analyze price trends by comparing current prices to 7, 30, and 90-day averages.",
            "Evaluate news sentiment for each news item (positive, negative, neutral).",
            "Look for correlations between news sentiment and price movements.",
            "Consider market volatility when making recommendations.",
            "Evaluate the credibility and impact of news sources.",
            "Analyze trading volume for unusual patterns indicating market sentiment.",
            "Look for divergences between news sentiment and price action, which may indicate market inefficiencies."
        ]
    
    def get_formatted(self) -> str:
        """Get formatted representation for prompt construction."""
        output = "## PROCEDURAL MEMORY (HOW TO ANALYZE DATA)\n\n"
        for i, procedure in enumerate(self.procedures, 1):
            output += f"{i}. {procedure}\n"
        return output

class LongTermMemory:
    """
    Stores facts, patterns, and knowledge about market behavior.
    Maintains learned facts with their confidence levels.
    """
    def __init__(self, max_facts: int = 30):
        self.facts: List[Fact] = []
        self.max_facts = max_facts
    
    def add_fact(self, fact: Fact):
        self.facts.append(fact)
        if len(self.facts) > self.max_facts:
            # Remove the lowest confidence fact
            self.facts.sort(key=lambda x: x.confidence)
            self.facts.pop(0)
    
    def get_formatted(self) -> str:
        """Get formatted representation for prompt construction."""
        output = "## LONG-TERM MEMORY (MARKET KNOWLEDGE)\n\n### Important Facts:\n"
        
        # Group facts by category
        categories = {}
        for fact in self.facts:
            if fact.category not in categories:
                categories[fact.category] = []
            categories[fact.category].append(fact)
        
        # Format facts by category, showing only the highest confidence facts to limit context
        for category, facts in categories.items():
            # Sort by confidence (highest first) and limit to 3 per category
            facts.sort(key=lambda x: x.confidence, reverse=True)
            top_facts = facts[:3]
            
            output += f"\n#### {category}:\n"
            for fact in top_facts:
                confidence_pct = int(fact.confidence * 100)
                output += f"- {fact.fact} (Confidence: {confidence_pct}%)\n"
        
        return output

class AutobiographicalMemory:
    """
    Stores past decisions, outcomes, and their rewards.
    Tracks the agent's decision history and performance.
    """
    def __init__(self, max_decisions: int = 20):
        self.decisions: List[Decision] = []
        self.max_decisions = max_decisions
    
    def add_decision(self, decision: Decision):
        self.decisions.append(decision)
        if len(self.decisions) > self.max_decisions:
            self.decisions.pop(0)  # Remove oldest decision
    
    def update_outcome(self, decision_id: str, outcome: str, reward: float):
        for decision in self.decisions:
            if decision.decision_id == decision_id:
                decision.outcome = outcome
                decision.reward = reward
                break
    
    def get_formatted(self) -> str:
        """Get formatted representation for prompt construction."""
        output = "## AUTOBIOGRAPHICAL MEMORY (PAST DECISIONS & OUTCOMES)\n\n"
        
        # Get most recent decisions with outcomes
        decisions_with_outcomes = [d for d in self.decisions if d.outcome is not None]
        decisions_with_outcomes.sort(key=lambda x: x.timestamp, reverse=True)
        
        if decisions_with_outcomes:
            output += "### Recent Decisions and Outcomes:\n"
            for decision in decisions_with_outcomes[:3]:  # Show last 3 decisions
                reward_str = f"{decision.reward:.2f}" if decision.reward is not None else "Unknown"
                output += f"- Decision: {decision.recommendation}\n"
                output += f"  Reasoning: {decision.reasoning}\n"
                output += f"  Outcome: {decision.outcome}\n"
                output += f"  Reward: {reward_str}\n\n"
        
        # Calculate overall performance if enough data
        if len(decisions_with_outcomes) >= 3:
            avg_reward = sum(d.reward or 0 for d in decisions_with_outcomes) / len(decisions_with_outcomes)
            output += f"Overall performance: Average reward {avg_reward:.2f} across {len(decisions_with_outcomes)} decisions.\n"
        
        return output

class WorkingMemory:
    """
    Stores current reasoning steps and analysis.
    Maintains the agent's active thought process.
    """
    def __init__(self, max_thoughts: int = 10):
        self.thoughts: List[Thought] = []
        self.max_thoughts = max_thoughts
    
    def add_thought(self, content: str):
        thought = Thought(content=content)
        self.thoughts.append(thought)
        if len(self.thoughts) > self.max_thoughts:
            self.thoughts.pop(0)  # Remove oldest thought
    
    def clear(self):
        self.thoughts = []
    
    def get_formatted(self) -> str:
        """Get formatted representation for prompt construction."""
        output = "## WORKING MEMORY (CURRENT ANALYSIS)\n\n"
        
        if not self.thoughts:
            output += "No current analysis in progress.\n"
        else:
            output += "### Current Thought Process:\n"
            for thought in self.thoughts:
                output += f"{thought.content}\n\n"
        
        return output

class ProspectiveMemory:
    """
    Stores considerations for future decisions.
    Maintains a list of important aspects to consider in upcoming analysis.
    """
    def __init__(self, max_considerations: int = 10):
        self.considerations: List[Consideration] = []
        self.max_considerations = max_considerations
    
    def add_consideration(self, text: str):
        consideration = Consideration(text=text)
        self.considerations.append(consideration)
        if len(self.considerations) > self.max_considerations:
            self.considerations.pop(0)  # Remove oldest consideration
    
    def get_formatted(self) -> str:
        """Get formatted representation for prompt construction."""
        output = "## PROSPECTIVE MEMORY (FUTURE CONSIDERATIONS)\n\n"
        
        if not self.considerations:
            output += "No specific future considerations noted.\n"
        else:
            output += "### Important Aspects to Consider:\n"
            for consideration in self.considerations:
                output += f"- {consideration.text}\n"
        
        return output