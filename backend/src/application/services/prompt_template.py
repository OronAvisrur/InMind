from typing import List, Dict, Any
from pydantic import BaseModel, Field

from src.domain.models.rag import RetrievedContext


class PromptTemplate(BaseModel):
    system_prompt: str
    user_prompt_template: str
    few_shot_examples: List[Dict[str, str]] = Field(default_factory=list)
    
    def format_user_prompt(self, **kwargs) -> str:
        return self.user_prompt_template.format(**kwargs)
    
    def build_full_prompt(self, **kwargs) -> str:
        user_prompt = self.format_user_prompt(**kwargs)
        
        if self.few_shot_examples:
            examples_text = "\n\n".join([
                f"Example {i+1}:\nUser: {ex['user']}\nAssistant: {ex['assistant']}"
                for i, ex in enumerate(self.few_shot_examples)
            ])
            return f"{self.system_prompt}\n\n{examples_text}\n\nNow respond to:\nUser: {user_prompt}"
        
        return f"{self.system_prompt}\n\nUser: {user_prompt}"


class RAGPromptTemplates:
    
    @staticmethod
    def get_recommendation_template() -> PromptTemplate:
        system_prompt = """You are an expert product recommendation assistant. Your task is to analyze the user's query and the retrieved product information, then provide personalized recommendations with clear reasoning.

                            Guidelines:
                            1. Consider the user's explicit requirements (price, features, category)
                            2. Prioritize products with higher relevance scores
                            3. Explain why each product matches the user's needs
                            4. Be concise but informative
                            5. If no products match well, explain why and suggest alternatives"""

        user_prompt_template = """User Query: {query}

                                Retrieved Products:
                                {products_context}

                                Based on the above information, recommend the best products for this user. Explain your reasoning step-by-step."""

        few_shot_examples = [
            {
                "user": "I need wireless headphones under $150",
                "assistant": "Based on your requirements, I recommend:\n\n1. Sony WH-CH520 ($98) - Best value option with 50-hour battery life and lightweight design\n2. JBL Tune 510BT ($129) - Excellent sound quality with JBL Pure Bass and fast charging\n\nBoth options are well under your $150 budget and offer wireless connectivity. The Sony provides longer battery life, while the JBL offers superior audio quality."
            },
            {
                "user": "Looking for a gaming laptop with RTX graphics",
                "assistant": "I recommend:\n\n1. ASUS ROG Strix G15 - Features RTX 4060, 15.6\" 144Hz display, ideal for AAA gaming\n2. MSI Katana 15 - RTX 4050, excellent cooling system, great for competitive gaming\n\nBoth laptops meet your RTX graphics requirement. The ASUS offers higher-tier GPU performance, while the MSI provides better thermal management for extended gaming sessions."
            }
        ]

        return PromptTemplate(
            system_prompt=system_prompt,
            user_prompt_template=user_prompt_template,
            few_shot_examples=few_shot_examples
        )
    
    @staticmethod
    def format_products_context(contexts: List[RetrievedContext]) -> str:
        if not contexts:
            return "No relevant products found."
        
        formatted_products = []
        for i, ctx in enumerate(contexts, 1):
            product = ctx.product
            relevance = f"{ctx.relevance_score:.2%}"
            
            product_info = f"""Product {i}:
                                - Name: {product.name}
                                - Category: {product.category}
                                - Price: ${product.price:.2f}
                                - Description: {product.description}
                                - Features: {', '.join(product.features)}
                                - Relevance Score: {relevance}"""
            
            formatted_products.append(product_info)
        
        return "\n\n".join(formatted_products)
    
    @staticmethod
    def get_comparison_template() -> PromptTemplate:
        system_prompt = """You are a product comparison expert. Compare the given products objectively, highlighting strengths and weaknesses of each."""

        user_prompt_template = """Compare these products:

                                {products_context}

                                Provide a detailed comparison focusing on: features, price, value for money, and use cases."""

        return PromptTemplate(
            system_prompt=system_prompt,
            user_prompt_template=user_prompt_template
        )