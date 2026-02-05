import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
# NEW (Correct for 2026)
from langchain_core.messages import HumanMessage, SystemMessage


# 1. Setup Gemini (The Free GPT alternative)
# Streamlit will pull the API key from your "Secrets" automatically
llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview", 
    google_api_key=st.secrets["GOOGLE_API_KEY"],
    temperature=0.7
)

st.set_page_config(page_title="Dapur AI", page_icon="🍲")
st.title("🍲 Dapur AI")
st.caption("Your Malaysian Dinner Decider")

# 2. Inventory Input
st.subheader("What's in your fridge today?")
protein = st.multiselect("Proteins", ["Chicken", "Ikan", "Beef", "Eggs", "Prawns", "Lamb"])
veggies = st.multiselect("Veggies", ["Sawi", "Carrot", "Cili Padi", "Kacang Panjang", "Bayam", "Potato"])
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
            
            response = llm.invoke([system_prompt, HumanMessage(content=user_prompt)])
            
            st.success("### Suggested Dish")
            #st.write(response.content)
            st.markdown(response.content)

# 4. Feedback (The beginning of your 'Memory' feature)
st.divider()
st.info("Did you like this suggestion?")
col1, col2 = st.columns(2)
with col1:
    if st.button("👍 Love it"): st.toast("Saved to your favorites!")
with col2:
    if st.button("👎 Not today"): st.toast("I'll suggest something else next time.")
