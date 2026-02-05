import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
# NEW (Correct for 2026)
from langchain_core.messages import HumanMessage, SystemMessage
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import re
from html.parser import HTMLParser

# Replit Brand Colors
REPLIT_DARK = "#0E1525"
REPLIT_NAVY = "#1C2333"
REPLIT_BLUE = "#0053A6"
REPLIT_TEXT = "#F5F9FC"
REPLIT_BORDER = "#3C445C"

def clean_response(text):
    """Clean HTML tags and unnecessary characters from response"""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove HTML entities
    text = re.sub(r'&[a-zA-Z0-9]+;', '', text)
    # Remove extra whitespace but keep line breaks
    text = re.sub(r'[ \t]+', ' ', text)
    # Remove excessive newlines (more than 2)
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Clean up markdown syntax for asterisks
    text = re.sub(r'\*{2,}', '**', text)
    return text.strip()

st.set_page_config(page_title="Dapur AI", page_icon="🍲", layout="centered")

# Custom CSS for the Replit Vibe
st.markdown(f"""
    <style>
    /* 1. Global Background and Text */
    .stApp {{
        background-color: {REPLIT_DARK};
        color: {REPLIT_TEXT};
    }}
    
    /* 2. Style the Input Cards (Containers) */
    div[data-testid="stVerticalBlock"] > div:has(div.stMultiSelect) {{
        background-color: {REPLIT_NAVY};
        padding: 20px;
        border-radius: 12px;
        border: 1px solid {REPLIT_BORDER};
        margin-bottom: 10px;
    }}

    /* 3. Style Buttons (The Blue Action Button) */
    div.stButton > button {{
        background-color: {REPLIT_BLUE} !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        height: 50px !important;
        width: 100% !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
        transition: all 0.2s ease;
    }}
    div.stButton > button:hover {{
        filter: brightness(1.2);
        box-shadow: 0 0 15px rgba(0, 83, 166, 0.4);
    }}

    /* 4. Style Multi-select & Input Boxes */
    div[data-baseweb="select"] > div {{
        background-color: {REPLIT_DARK} !important;
        border: 1px solid {REPLIT_BORDER} !important;
    }}
    
    /* 5. Hide Streamlit Branding */
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    #MainMenu {{visibility: hidden;}}

    /* 6. Typography */
    h1, h2, h3 {{
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif;
    }}
    
    /* 7. Button Text Visibility in Dark Mode */
    button {{
        color: {REPLIT_TEXT} !important;
    }}
    button:hover {{
        color: #FFFFFF !important;
    }}
    
    /* 8. Response Container Styling */
    .response-container {{
        background: linear-gradient(135deg, {REPLIT_NAVY} 0%, {REPLIT_DARK} 100%);
        border: 2px solid {REPLIT_BLUE};
        border-radius: 12px;
        padding: 30px;
        margin-top: 20px;
        box-shadow: 0 8px 32px rgba(0, 83, 166, 0.2);
    }}
    
    .response-container h2 {{
        color: {REPLIT_BLUE} !important;
        margin-top: 0;
        border-bottom: 2px solid {REPLIT_BLUE};
        padding-bottom: 15px;
    }}
    
    .response-container h3 {{
        color: #FFFFFF !important;
        margin-top: 20px;
    }}
    
    .response-container p {{
        color: {REPLIT_TEXT} !important;
        line-height: 1.6;
    }}
    
    .response-container ol, .response-container ul {{
        color: {REPLIT_TEXT} !important;
    }}
    
    .response-container li {{
        color: {REPLIT_TEXT} !important;
        margin-bottom: 8px;
    }}
    
    .response-container strong {{
        color: #FFFFFF !important;
    }}
    
    .response-container em {{
        color: #A0AEC0;
    }}
    
    .response-container hr {{
        border-color: {REPLIT_BORDER};
    }}
    </style>
    """, unsafe_allow_html=True)

# 1. Setup Gemini (The Free GPT alternative)
# Streamlit will pull the API key from your "Secrets" automatically
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", 
    google_api_key=st.secrets["GOOGLE_API_KEY"],
    temperature=0.7
)

# Add retry logic wrapper
@retry(
    stop=stop_after_attempt(3), 
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
    reraise=True
)
def get_recipe_suggestion(system_prompt, user_message):
    """Get recipe suggestion with retry logic"""
    return llm.invoke([system_prompt, user_message])

st.title("🍲 Dapur AI")
st.markdown("---")

# Initialize session state for protein and vegetable selection
if "selected_proteins" not in st.session_state:
    st.session_state.selected_proteins = []
if "selected_veggies" not in st.session_state:
    st.session_state.selected_veggies = []

# 2. Inventory Input
with st.container():
    st.subheader("What's in your fridge today?")
    
    # Icon-based Protein Selection
    st.write("**Proteins** 🥩")
    protein_options = {
        "🐔 Chicken": "Chicken",
        "🐟 Ikan": "Ikan",
        "🥩 Beef": "Beef",
        "🥚 Eggs": "Eggs",
        "🦐 Prawns": "Prawns",
        "🐑 Lamb": "Lamb"
    }
    
    cols = st.columns(6)
    for idx, (emoji_label, protein_name) in enumerate(protein_options.items()):
        with cols[idx]:
            is_selected = protein_name in st.session_state.selected_proteins
            button_style = "✓" if is_selected else ""
            if st.button(f"{emoji_label}\n{button_style}", use_container_width=True, key=f"protein_{protein_name}"):
                if protein_name in st.session_state.selected_proteins:
                    st.session_state.selected_proteins.remove(protein_name)
                else:
                    st.session_state.selected_proteins.append(protein_name)
                st.rerun()
    
    protein = st.session_state.selected_proteins
    
    # Icon-based Vegetable Selection
    st.write("**Vegetables** 🥗")
    veggie_options = {
        "🥬 Sawi": "Sawi",
        "🥕 Carrot": "Carrot",
        "🌶️ Cili Padi": "Cili Padi",
        "🫘 Kacang Panjang": "Kacang Panjang",
        "🥗 Bayam": "Bayam",
        "🥔 Potato": "Potato"
    }
    
    cols_veggie = st.columns(6)
    for idx, (emoji_label, veggie_name) in enumerate(veggie_options.items()):
        with cols_veggie[idx]:
            is_selected = veggie_name in st.session_state.selected_veggies
            button_style = "✓" if is_selected else ""
            if st.button(f"{emoji_label}\n{button_style}", use_container_width=True, key=f"veggie_{veggie_name}"):
                if veggie_name in st.session_state.selected_veggies:
                    st.session_state.selected_veggies.remove(veggie_name)
                else:
                    st.session_state.selected_veggies.append(veggie_name)
                st.rerun()
    
    veggies = st.session_state.selected_veggies
    
    pantry = st.text_input("Other Ingredients (e.g., Santan, Serai, Bunga Kantan)")

    mode = st.select_slider("Cooking Effort", options=["Penat (Quick)", "Normal", "Rajin (Authentic)"])

# 3. Generating the Suggestion
if st.button("What should I cook?", use_container_width=True):
    if not protein and not veggies:
        st.error("Please select at least something from your fridge!")
    else:
        with st.spinner("Chef Gemini is thinking..."):
            system_prompt = SystemMessage(content="""You are an expert Malaysian Home Chef. 
            Suggest ONE dish based on the ingredients provided. 
            If mode is 'Penat', suggest a 15-min meal. 
            If 'Rajin', suggest a traditional slow-cooked dish. 
            Always explain why this dish fits the ingredients.""")
            
            user_prompt = f"Ingredients: {protein}, {veggies}, {pantry}. Mode: {mode}."
            
            try:
                response = get_recipe_suggestion(system_prompt, HumanMessage(content=user_prompt))
                
                # Clean the response and display it
                cleaned_content = clean_response(response.content)
                st.markdown(f'<div class="response-container">{cleaned_content}</div>', unsafe_allow_html=True)
            except Exception as e:
                error_msg = str(e)
                if "API key" in error_msg or "authentication" in error_msg.lower():
                    st.error("🔑 Authentication error: Please check your Google API key in Streamlit secrets.")
                elif "quota" in error_msg.lower():
                    st.error("⚠️ API quota exceeded: Please try again later.")
                elif "model" in error_msg.lower():
                    st.error("🤖 Model unavailable: The Gemini model is temporarily unavailable.")
                else:
                    st.error(f"Failed to get recipe suggestion after retries. Please try again.\\n\\nError: {error_msg}")

# 4. Feedback (The beginning of your 'Memory' feature)
st.divider()
st.info("Did you like this suggestion?")
col1, col2 = st.columns(2)
with col1:
    if st.button("👍 Love it"): st.toast("Saved to your favorites!")
with col2:
    if st.button("👎 Not today"): st.toast("I'll suggest something else next time.")
