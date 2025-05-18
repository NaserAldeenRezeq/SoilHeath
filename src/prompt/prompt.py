# -*- coding: utf-8 -*-
class FarmAssistantPromptBuilder:
    @staticmethod
    def build_prompt(soil_report: str, farmer_input: str) -> str:
        return (
            f"You are a smart and helpful farm assistant AI. "
            f"Your job is to analyze the soil composition and suggest improvements. "
            f"The farmer will provide breeding elements such as hydrogen, nitrogen, and carbon.\n"
            f"{soil_report}\n\n"
            f"Farmer Input: {farmer_input}\n"
            f"Assistant Recommendation:"
        )

if __name__ == "__main__":
    # Example usage
    soil_report = "The soil has been showing poor crop yield for the last two seasons."
    farmer_input = "Hydrogen: low, Nitrogen: medium, Carbon: high"
    prompt = FarmAssistantPromptBuilder.build_prompt(soil_report, farmer_input)
    print(prompt)
