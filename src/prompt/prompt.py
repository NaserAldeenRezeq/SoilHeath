"""
wirte Docstring

"""

# -*- coding: utf-8 -*-
class FarmAssistantPromptBuilder:
    @staticmethod
    def build_prompt(context: str, user_message: str = "", weather: str = "") -> str:
        """
        Builds a professional agricultural assistance prompt combining:
        - Context about the farm situation
        - Soil composition data
        - Optional specific user questions
        
        Args:
            context: Background information about the farm's condition and history
            soil_data: Soil element measurements and observations
            user_message: Specific questions or notes from the farmer
            
        Returns:
            str: A well-structured prompt for agricultural recommendations
        """
        return (
            "You are an expert agricultural AI assistant with deep knowledge in soil science, "
            "crop nutrition, and sustainable farming practices. Analyze the following information "
            "and provide a professional, actionable recommendation:\n\n"

            "**RAG Context**:\n"
            f"{context}\n\n"

            "**Soil Composition Analysis**:\n"
            f"{user_message}"

            "**Weather Status**:\n"
            f"{weather}"

            "Provide a detailed recommendation addressing:\n"
            "1. Soil health assessment based on the element levels\n"
            "2. Specific nutrient adjustments needed\n"
            "3. Recommended amendments or fertilizers\n"
            "4. Any crop-specific considerations\n"
            "5. Long-term soil management suggestions\n\n"

            "Structure your response with clear headings and prioritize "
            "sustainable, cost-effective solutions:\n\n"
            "**Professional Recommendation**:"
        )
