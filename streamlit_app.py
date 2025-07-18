import streamlit as st
import replicate
import os

# Ensure the Replicate API token is set
if 'REPLICATE_API_TOKEN' in st.secrets:
    replicate_api = st.secrets['REPLICATE_API_TOKEN']
else:
    replicate_api = st.text_input('Enter Replicate API token:', type='password')
os.environ['REPLICATE_API_TOKEN'] = replicate_api

# Set up page configuration
st.set_page_config(page_title="Personalized Fitness Assistant")

# Check session state
if "page" not in st.session_state:
    st.session_state.page = "form"

# Step 1: Personal Information Form
if st.session_state.page == "form":
    st.title("Create Your Fitness Profile")

    with st.form("user_info_form"):
        weight = st.number_input("Weight (kg):", min_value=1.0, step=0.1)
        height = st.number_input("Height (m):", min_value=0.5, step=0.01)
        age = st.number_input("Age:", min_value=1)
        gender = st.selectbox("Gender:", ["Male", "Female", "Other"])
        sleep_time = st.slider("Sleep Time (hours):", 0.0, 24.0, 8.0, 0.5)
        days_free = st.multiselect("Days You're Free:", ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])

        complete = st.form_submit_button("Complete")
    
    if complete:
        # Save user data to session state
        st.session_state.user_data = {
            "weight": weight,
            "height": height,
            "age": age,
            "gender": gender,
            "sleep_time": sleep_time,
            "days_free": days_free,
            "bmi": weight / (height ** 2)
        }
        st.session_state.page = "chat"
        st.rerun()

# Step 2: Chatbot Page (Simplified)
elif st.session_state.page == "chat":
    st.title("Personalized Fitness Chatbot 💬")

    # Display user profile info
    st.write(f"**BMI**: {round(st.session_state.user_data['bmi'], 2)}")
    st.write(f"**Free Days**: {', '.join(st.session_state.user_data['days_free'])}")
    st.write(f"**Sleep Time**: {st.session_state.user_data['sleep_time']} hours")

    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "fitness instructor",
            "content": "Hi! How can I assist you with your fitness journey today?"
        }]
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Function to generate response using LLaMA 3 model via Replicate API
    def generate_llama_response(prompt_input):
        try:
            response = replicate.run(
                "a16z-infra/llama13b-v2-chat:latest",  # Replace with the correct model reference
                input={"prompt": f"{prompt_input}\nAssistant:", "temperature": 0.7, "max_length": 150}
            )
            return ''.join(response)
        except replicate.exceptions.ReplicateError as e:
            st.error(f"Error: {e}")
            return "Sorry, there was an error processing your request. Please try again later."

    # Get user input and generate LLaMA response
    if prompt := st.chat_input("Ask me anything about your fitness plan!"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("fitness instructor"):
            with st.spinner("Thinking..."):
                reply = generate_llama_response(prompt)
                st.write(reply)
                st.session_state.messages.append({"role": "fitness instructor", "content": reply})
