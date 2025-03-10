import os
import pickle
import logging
from typing import List, Optional
from langchain_openai import AzureChatOpenAI
from langchain.schema import HumanMessage, AIMessage
import pandas as pd

from .memory_systems import (
    SensoryMemory, 
    ShortTermMemory, 
    ProceduralMemory,
    WorkingMemory, 
    LongTermMemory, 
    AutobiographicalMemory, 
    ProspectiveMemory
)
from .data_structures import NewsItem, PriceData, Fact, Decision

logger = logging.getLogger(__name__)

class LLMAgent:
    def __init__(self, 
                 api_key: Optional[str] = None,
                 azure_endpoint: Optional[str] = None,
                 api_version: str = "2023-05-15",
                 deployment_name: str = "gpt-35-turbo",
                 temperature: float = 0.7):
        """
        Initialize the LLM agent with multiple memory systems.
        """
        # Initialize memory systems
        self.sensory_memory = SensoryMemory()
        self.short_term_memory = ShortTermMemory()
        self.procedural_memory = ProceduralMemory()
        self.long_term_memory = LongTermMemory()
        self.autobiographical_memory = AutobiographicalMemory()
        self.working_memory = WorkingMemory()
        self.prospective_memory = ProspectiveMemory()
        
        # Initialize the language model
        self.llm = AzureChatOpenAI(
            openai_api_key=api_key,
            azure_endpoint=azure_endpoint,
            api_version=api_version,
            deployment_name=deployment_name,
            temperature=temperature
        )
        
        # Set the system prompt with extra instruction regarding holding too many times.
        self.system_prompt = """
You are an advanced AI financial analyst with multiple memory systems.
Your goal is to provide investment recommendations based on news and price data.
As you process information, you will build knowledge and learn from your past decisions.
Think step by step and show your reasoning process before making final recommendations.

You have the following memory systems:
1. Sensory Memory: Current market conditions (news and prices)
2. Short-Term Memory: Recent market history with statistical features
3. Procedural Memory: Methods for analyzing data
4. Long-Term Memory: Facts and knowledge about market behavior
5. Autobiographical Memory: Your past decisions and their outcomes
6. Working Memory: Your current analysis
7. Prospective Memory: Important aspects to consider in the future

When making recommendations, consider all these memory systems and explain your reasoning.
**Important:** If you have recommended "Hold" in several consecutive recommendations, you must take a decisive position in your next recommendation, choosing either "Long" or "Short".
        """
        
        # Set the file path for memory persistence
        self.memory_filepath = "data/memory/agent_memory.pkl"
        self.load_memory()

    def _build_full_prompt(self, query: str) -> str:
        """
        Build a complete prompt by combining all memory systems.
        """
        prompt_parts = [
            self.system_prompt,
            self.sensory_memory.get_formatted(),
            self.short_term_memory.get_formatted(),
            self.procedural_memory.get_formatted(),
            self.long_term_memory.get_formatted(),
            self.autobiographical_memory.get_formatted(),
            self.working_memory.get_formatted(),
            self.prospective_memory.get_formatted(),
            f"\n## NEW QUERY\n{query}\n\n## RESPONSE\nLet me think through this step by step:"
        ]
        return "\n\n".join(prompt_parts)
    
    def react_step(self, query: str) -> str:
        """
        Execute a single reasoning step.
        """
        full_prompt = self._build_full_prompt(query)
        response = self.llm.invoke([HumanMessage(content=full_prompt)])
        self.working_memory.add_thought(response.content)
        logger.info(f"Updating memory WorkingMemory: Added thought: '{response.content}'")
        return response.content
    
    def make_recommendation(self, query: str) -> Decision:
        """
        Make a financial recommendation based on the query.
        """
        # Clear working memory and log it.
        self.working_memory.clear()
        logger.info("Clearing WorkingMemory")
        
        # First step: analyze the query
        self.react_step(f"Analyze the latest news and price data to answer: {query}")
        
        # Second step: make a recommendation with explicit instructions
        recommendation_prompt = f"""
Based on your previous analysis, make a final recommendation regarding: {query}

Your response should be structured as, NEVER RECOMMEND HOLD IT CAN BE NEGATIVE FOR THE USER:
RECOMMENDATION: [Choose one of: Long, Short]
CONFIDENCE: [Numeric value between 0-1]
REASONING: [Concise summary of key factors that led to this recommendation]

        """
        full_prompt = self._build_full_prompt(recommendation_prompt)
        recommendation_response = self.llm.invoke([HumanMessage(content=full_prompt)])
        response_text = recommendation_response.content
        
        recommendation = ""
        confidence = 0.5  # Default value
        reasoning = ""
        
        for line in response_text.split('\n'):
            if line.startswith("RECOMMENDATION:"):
                extracted_recommendation = line.replace("RECOMMENDATION:", "").strip()
                if extracted_recommendation in ["Long", "Short"]:
                    recommendation = extracted_recommendation
                else:
                    # If the LLM fails to provide a valid recommendation, force one based on trends
                    recommendation = "Long" if confidence > 0.5 else "Short"

            elif line.startswith("CONFIDENCE:"):
                confidence_str = line.replace("CONFIDENCE:", "").strip()
                try:
                    confidence = float(confidence_str)
                except ValueError:
                    confidence = 0.7  # Default to moderate confidence if parsing fails

            elif line.startswith("REASONING:"):
                reasoning = line.replace("REASONING:", "").strip()

        # Ensure a decision is always made
        if recommendation == "":
            recommendation = "Long" if confidence > 0.5 else "Short"
        
        decision = Decision(
            recommendation=recommendation,
            confidence=confidence,
            reasoning=reasoning
        )
        self.autobiographical_memory.add_decision(decision)
        logger.info(f"Updating memory AutobiographicalMemory: Added decision with recommendation '{recommendation}'")
        return decision
    
    def process_feedback(self, decision_id: str, outcome: str, reward: float) -> str:
        """
        Process feedback on a previous decision and learn from it.
        """
        # Update the decision outcome in autobiographical memory and log it.
        self.autobiographical_memory.update_outcome(decision_id, outcome, reward)
        logger.info(f"Updating memory AutobiographicalMemory: Updated decision {decision_id} with outcome '{outcome}' and reward {reward}")
        
        # Generate a learning prompt
        feedback_prompt = f"""
I received feedback on my recommendation (ID: {decision_id}):
Outcome: {outcome}
Reward: {reward}

Based on this feedback, what's one important fact I should remember for future decisions?
Format your response as:
NEW FACT: [concise statement of a fact to remember]
CATEGORY: [category for this fact]
CONFIDENCE: [numeric value between 0-1]
        """
        full_prompt = self._build_full_prompt(feedback_prompt)
        learning_response = self.llm.invoke([HumanMessage(content=full_prompt)])
        response_text = learning_response.content
        
        fact_text = ""
        category = "general"
        confidence = 0.5
        
        for line in response_text.split('\n'):
            if line.startswith("NEW FACT:"):
                fact_text = line.replace("NEW FACT:", "").strip()
            elif line.startswith("CATEGORY:"):
                category = line.replace("CATEGORY:", "").strip()
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.replace("CONFIDENCE:", "").strip())
                except ValueError:
                    pass
        
        if fact_text:
            new_fact = Fact(
                fact=fact_text,
                source=f"Feedback on decision {decision_id}",
                confidence=confidence,
                category=category
            )
            self.long_term_memory.add_fact(new_fact)
            logger.info(f"Updating memory LongTermMemory: Added fact: '{new_fact.fact}'")
            consideration = f"Consider the outcome of similar situations to decision {decision_id} ({fact_text})"
            self.prospective_memory.add_consideration(consideration)
            logger.info(f"Updating memory ProspectiveMemory: Added consideration: '{consideration}'")
        
        return learning_response.content
    
    def update_with_news(self, news_items: List[NewsItem]):
        """
        Update the agent's memory with news items.
        """
        for item in news_items:
            self.sensory_memory.add_news(item)
            logger.info(f"Updating memory SensoryMemory: Added news item: '{item.text}'")
            self.short_term_memory.add_news(item)
            logger.info(f"Updating memory ShortTermMemory: Added news item: '{item.text}'")
    
    def update_with_prices(self, price_data: List[PriceData]):
        """
        Update the agent's memory with price data.
        """
        for item in price_data:
            self.sensory_memory.add_price(item)
            logger.info(f"Updating memory SensoryMemory: Added price data for asset '{item.asset}' on '{item.date}'")
            self.short_term_memory.add_price(item)
            logger.info(f"Updating memory ShortTermMemory: Added price data for asset '{item.asset}' on '{item.date}'")

    def save_memory(self):
        """
        Persist the memory systems to disk.
        """
        memory_data = {
            "sensory_memory": self.sensory_memory,
            "short_term_memory": self.short_term_memory,
            "procedural_memory": self.procedural_memory,
            "long_term_memory": self.long_term_memory,
            "autobiographical_memory": self.autobiographical_memory,
            "working_memory": self.working_memory,
            "prospective_memory": self.prospective_memory
        }
        with open(self.memory_filepath, "wb") as f:
            pickle.dump(memory_data, f)
        logger.info("Agent memory saved successfully.")

    def load_memory(self):
        """
        Load previously saved memory systems from disk, if available.
        """
        if os.path.exists(self.memory_filepath):
            with open(self.memory_filepath, "rb") as f:
                memory_data = pickle.load(f)
            self.sensory_memory = memory_data.get("sensory_memory", self.sensory_memory)
            self.short_term_memory = memory_data.get("short_term_memory", self.short_term_memory)
            self.procedural_memory = memory_data.get("procedural_memory", self.procedural_memory)
            self.long_term_memory = memory_data.get("long_term_memory", self.long_term_memory)
            self.autobiographical_memory = memory_data.get("autobiographical_memory", self.autobiographical_memory)
            self.working_memory = memory_data.get("working_memory", self.working_memory)
            self.prospective_memory = memory_data.get("prospective_memory", self.prospective_memory)
            logger.info("Agent memory loaded from file.")
        else:
            logger.info("No previous memory file found. Starting with empty memory.")
