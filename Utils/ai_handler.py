import google.generativeai as genai

# Configure API Key
genai.configure(
    api_key="Your_Api_Key"
)

# Use the 'latest' alias to ensure you are always on the current Gemini 3 engine
# 'gemini-3-flash-latest' is highly recommended for data analysis due to speed/cost.
model = genai.GenerativeModel("gemini-3-flash-preview")

def get_ai_response(columns, sample, summary, user_query):
    try:
        # Structured prompt for better data parsing
        prompt = f"""
        You are a professional AI data analyst.
        
        ### Context
        Dataset Columns: {columns}
        Summary Statistics: {summary}
        
        ### Sample Data (First few rows)
        {sample}
        
        ### Task
        Analyze the data and answer this question: "{user_query}"
        
        ### Constraints
        - Provide concise, high-impact insights.
        - Do not provide Python/SQL code unless requested.
        - Use bullet points for readability.
        """

        # Using generation_config to ensure the AI stays focused
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,  # Lower temperature for more factual data analysis
            )
        )

        return response.text

    except Exception as e:
        # Error handling to catch specific API version mismatches
        return f"⚠️ AI Error: {str(e)}"
