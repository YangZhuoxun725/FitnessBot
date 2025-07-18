import streamlit as st
import replicate
import os

# Streamlit page configuration
st.set_page_config(page_title="Personalized Fitness Assistant")

# Define available days for free
DAYS_FREE_OPTIONS = ["Sunday Morning", "Sunday Evening", "Monday Morning", "Monday Evening", "Tuesday Morning", 
                     "Tuesday Evening", "Wednesday Morning", "Wednesday Evening", "Thursday Morning", "Thursday Evening", 
                     "Friday Morning", "Friday Evening", "Saturday Morning", "Saturday Evening"]

# Set session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "form"

# --------------------------------------------------------
# Step 1: Personal Information Form
if st.session_state.page == "form":
    st.title("Create Your Fitness Profile")

    with st.form("user_info_form"):
        weight = st.number_input("Weight (kg):", min_value=1.0, step=0.1)
        height = st.number_input("Height (m):", min_value=0.5, step=0.01)
        age = st.number_input("Age:", min_value=1)
        gender = st.selectbox("Gender:", ["Male", "Female", "Other"])
        sleep_time = st.slider("Sleep Time (hours):", 0.0, 24.0, 8.0, 0.5)
        days_free = st.multiselect("Days You're Free:", DAYS_FREE_OPTIONS)
        
        # New fields for fitness goals
        goal = st.selectbox("What is your primary fitness goal?", ["Lose weight", "Build muscle", "Improve stamina", "Increase flexibility"])
        fitness_level = st.selectbox("What's your current fitness level?", ["Beginner", "Intermediate", "Advanced"])

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
            "goal": goal,
            "fitness_level": fitness_level,
            "bmi": weight / (height ** 2)
        }
        st.session_state.page = "chat"
        st.experimental_rerun()

# --------------------------------------------------------
# Step 2: Chatbot Page
elif st.session_state.page == "chat":
    st.title("Personalized Fitness Chatbot 💬")

    # Sidebar for settings and API token input
    with st.sidebar:
        if 'REPLICATE_API_TOKEN' in st.secrets:
            st.success('API key already provided!', icon='✅')
            replicate_api = st.secrets['REPLICATE_API_TOKEN']
        else:
            replicate_api = st.text_input('Enter Replicate API token:', type='password')
        
        os.environ['REPLICATE_API_TOKEN'] = replicate_api

        # Display user profile info
        st.write(f"**BMI**: {round(st.session_state.user_data['bmi'], 2)}")
        st.write(f"**Free Days**: {', '.join(st.session_state.user_data['days_free'])}")
        st.write(f"**Goal**: {st.session_state.user_data['goal']}")
        st.write(f"**Fitness Level**: {st.session_state.user_data['fitness_level']}")
        
        st.button('Back to Form', on_click=lambda: st.session_state.update({"page": "form"}))

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "fitness instructor",
            "content": "Hi! How can I assist you with your fitness journey today?"
        }]
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Function to generate a response from Replicate API
    def generate_llama2_response(prompt_input):
        base_prompt = (
            f"You are a fitness instructor. The user has the following details:\n"
            f"Weight: {st.session_state.user_data['weight']} kg, Height: {st.session_state.user_data['height']} m, "
            f"Age: {st.session_state.user_data['age']}, Gender: {st.session_state.user_data['gender']}, "
            f"Sleep Time: {st.session_state.user_data['sleep_time']} hours, Free Days: {', '.join(st.session_state.user_data['days_free'])}, "
            f"Goal: {st.session_state.user_data['goal']}, Fitness Level: {st.session_state.user_data['fitness_level']}.\n"
            "Create a personalized workout schedule and give advice accordingly."
        )
        chat_history = base_prompt
        for msg in st.session_state.messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            chat_history += f"\n{role}: {msg['content']}"
        
        # Handle API request to Replicate
        try:
            response = replicate.run(
                "a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5",
                input={"prompt": f"{chat_history}\nAssistant:", "temperature": 0.1, "top_p": 0.9, "max_length": 150, "repetition_penalty": 1}
            )
            return ''.join(response)
        except Exception as e:
            st.error(f"Error generating response from Replicate: {str(e)}")
            st.write(f"**Detailed Error**: {str(e)}")  # This will log the full error message to Streamlit.
            return "Sorry, there was an error generating your workout plan. Please try again later."

    # Get user input and provide a response
    if prompt := st.chat_input("Ask me anything about your fitness plan!", disabled=not replicate_api):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("fitness instructor"):
            with st.spinner("Generating your personalized workout plan... please wait!"):
                reply = generate_llama2_response(prompt)
                st.write(reply)
                st.session_state.messages.append({"role": "fitness instructor", "content": reply})

