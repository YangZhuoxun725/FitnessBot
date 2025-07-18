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

    # Function to generate response using LLaMA 3 via Replicate API
    def generate_llama_response(prompt_input):
        base_prompt = (
            f"You are a fitness instructor. Use the following user data: "
            f"Weight: {st.session_state.user_data['weight']} kg, "
            f"Height: {st.session_state.user_data['height']} m, "
            f"Age: {st.session_state.user_data['age']}, "
            f"Gender: {st.session_state.user_data['gender']}, "
            f"Sleep Time: {st.session_state.user_data['sleep_time']} hrs, "
            f"Free Days: {', '.join(st.session_state.user_data['days_free'])}. "
            "Create personalized workout plans, give advice, and ask for more goals."
        )
        
        chat_history = base_prompt
        for msg in st.session_state.messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            chat_history += f"\n{role}: {msg['content']}"
        
        response = replicate.run(
            "a16z-infra/llama3-chat:latest",  # LLaMA 3 model endpoint
            input={"prompt": f"{chat_history}\nAssistant:", "temperature": 0.7, "max_length": 150}
        )
        return ''.join(response)

    # Get user input and generate LLaMA 3 response
    if prompt := st.chat_input("Ask me anything about your fitness plan!"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("fitness instructor"):
            with st.spinner("Thinking..."):
                reply = generate_llama_response(prompt)
                st.write(reply)
                st.session_state.messages.append({"role": "fitness instructor", "content": reply})
