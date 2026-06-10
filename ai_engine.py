import os
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

# Default Gemini API Key provided by the user
DEFAULT_API_KEY = ""

def get_api_key(user_key=None):
    """Resolves which API key to use (User inputted key > Env variable > Default key)"""
    if user_key and user_key.strip():
        return user_key.strip()
    
    env_key = os.environ.get("GEMINI_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()
        
    return DEFAULT_API_KEY

def configure_api(api_key):
    """Configures the google-generativeai package"""
    genai.configure(api_key=api_key)

def get_eco_coach_response(chat_history, user_message, user_key=None):
    """
    Sends the user message to the Gemini Eco-Coach chatbot and returns the response.
    chat_history should be a list of dicts with keys 'role' ('user' or 'model') and 'parts' (string list or text).
    """
    key = get_api_key(user_key)
    configure_api(key)
    
    system_instruction = (
        "You are EchoStep AI, a friendly, encouraging, and highly knowledgeable Eco-Coach. "
        "Your mission is to help users track, calculate, and systematically reduce their personal carbon footprint. "
        "Use science-backed facts to support your claims and give realistic, highly practical tips for daily life. "
        "Structure your answers with bullet points and bold text where relevant so they are easy to scan. "
        "Keep your tone positive and gamified: praise the user for small efforts, and never sound preachy or judgmental. "
        "Always focus on concrete steps, like taking public transit, choosing plant-based meals, or adjusting thermostat settings."
    )
    
    try:
        model = genai.GenerativeModel(
            model_name="gemini-3.5-flash",
            system_instruction=system_instruction
        )
        
        # Convert streamlit chat history format to Gemini SDK history format
        gemini_history = []
        for chat in chat_history:
            role = "user" if chat["role"] == "user" else "model"
            gemini_history.append({
                "role": role,
                "parts": [chat["content"]]
            })
            
        chat_session = model.start_chat(history=gemini_history)
        response = chat_session.send_message(user_message)
        return response.text
        
    except Exception as e:
        return f"Error connecting to Eco-Coach: {str(e)}. Please check your API key configuration in the sidebar."

def generate_action_plan(activity_summary_df, active_goals_df, user_key=None):
    """
    Generates a personalized, prioritized Carbon Footprint Reduction Action Plan 
    based on the user's historical logging data and goals.
    """
    key = get_api_key(user_key)
    configure_api(key)
    
    # Compile a text summary of user metrics for the LLM
    if activity_summary_df.empty:
        summary_text = "The user has not logged any activities yet. Provide a general guide on how to get started with sustainable living."
    else:
        # Group by category to see highest emissions
        by_category = activity_summary_df.groupby('category')['emissions'].sum().to_dict()
        total_emissions = sum(by_category.values())
        
        # Details of the last 10 logs
        last_logs = activity_summary_df.head(10)[['date', 'category', 'activity_type', 'amount', 'emissions']].to_string(index=False)
        
        summary_text = f"User Carbon Profile:\n"
        summary_text += f"- Total Logged Emissions: {total_emissions:.2f} kg CO2e\n"
        summary_text += f"- Emissions by Category:\n"
        for cat, val in by_category.items():
            pct = (val / total_emissions) * 100 if total_emissions > 0 else 0
            summary_text += f"  * {cat}: {val:.2f} kg CO2e ({pct:.1f}%)\n"
            
        summary_text += f"\nRecent Activities Logged:\n{last_logs}\n"
        
    if not active_goals_df.empty:
        goals_list = active_goals_df[['category', 'target_reduction_pct', 'target_date', 'status']].to_string(index=False)
        summary_text += f"\nActive Reduction Goals:\n{goals_list}\n"
    else:
        summary_text += "\nNo active carbon goals set yet.\n"
        
    prompt = (
        f"You are the EchoStep AI Recommendation Engine. Analyze the user's carbon footprint profile and generate a comprehensive, personalized carbon reduction plan.\n\n"
        f"{summary_text}\n\n"
        f"Format your response as a beautifully structured Markdown report with the following specific sections:\n"
        f"1. **Executive Summary**: A brief, encouraging 3-sentence summary of their current footprint and largest impact areas.\n"
        f"2. **Sector Analysis**: Break down their emissions (Transport, Diet, Utilities) and explain what these numbers mean in real-world equivalents (e.g., matching emissions to number of trees needed to offset or smartphone charges).\n"
        f"3. **Prioritized Action Steps**: Provide 3-5 specific, realistic, and actionable recommendations. Group them by 'Low Effort' (e.g., unplugging idle devices), 'Medium Effort' (e.g., meal prepping vegan lunches), and 'High Impact' (e.g., commuting via train instead of petrol car).\n"
        f"4. **Smart Goal Strategy**: If the user has active goals, suggest how to achieve them. If not, recommend two targets they should set.\n"
        f"Keep the language highly engaging, professional, and clear."
    )
    
    try:
        model = genai.GenerativeModel("gemini-3.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating recommendations: {str(e)}. Please check your API key configuration in the sidebar."
