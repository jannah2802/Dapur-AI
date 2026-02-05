import streamlit as st
from langchain_openai import AzureChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

# 1. Setup Azure OpenAI (Use your existing deployment details)
llm = AzureChatOpenAI(
    azure_deployment="your-deployment-name",
    api_version="2023-05-15",
    azure_endpoint="your-azure-endpoint",
    api_key="your-api-key"
)

st.title("🍲 Dapur AI")
st.subheader("What's in your fridge today?")

# 2. Inventory Input
col1, col2 = st.columns(2)
with col1:
    protein = st.multiselect("Proteins", ["Chicken", "Ikan Kembung", "Beef", "Eggs", "Prawns"])
with col2:
    veggies = st.multiselect("Veggies", ["Sawi", "Carrot", "Cili Padi", "Kacang Panjang", "Tomato"])

pantry = st.text_input("Other (e.g., Santan, Belacan, Oyster Sauce)")
mode = st.radio("Cooking Mode", ["Quick & Easy", "Authentic Malaysian"])

# 3. The Logic
if st.button("Decide Dinner for Me!"):
    if not protein:
        st.warning("Please add at least one protein!")
    else:
        system_msg = SystemMessage(content="""You are a Malaysian Home Chef. 
        Suggest a dish based on ingredients. If 'Quick' mode, suggest something under 20 mins. 
        If 'Authentic', suggest a classic Malay dish.""")
        
        user_input = f"I have: {protein}, {veggies}, and {pantry}. Mode: {mode}. Suggest 1 dish with simple steps."
        
        response = llm.invoke([system_msg, HumanMessage(content=user_input)])
        
        st.success(f"### Suggestion: {response.content}")
