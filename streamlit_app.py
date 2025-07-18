import streamlit as st

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

    # Function to generate dynamic responses based on user data
    def generate_response(user_input):
        # Basic response generation based on user data
        if "workout" in user_input.lower():
            if st.session_state.user_data["age"] < 30:
                return "I recommend focusing on strength training with compound exercises. You could try deadlifts, squats, and bench presses."
            elif st.session_state.user_data["age"] >= 30:
                return "At your age, it's important to include mobility exercises like yoga or stretching along with strength training to avoid injuries."
        
        elif "bmi" in user_input.lower():
            bmi = st.session_state.user_data["bmi"]
            if bmi < 18.5:
                return "Your BMI suggests you might be underweight. It’s important to focus on gaining muscle through strength training and a high-protein diet."
            elif 18.5 <= bmi < 24.9:
                return "Your BMI is in the healthy range. Keep up the good work! You can focus on maintaining this level of fitness."
            elif bmi >= 30:
                return "Your BMI suggests you might be overweight. A combination of cardio exercises and strength training could help reduce body fat."

        elif "diet" in user_input.lower():
            return "For a balanced diet, focus on whole foods, lean proteins, vegetables, fruits, and healthy fats. Stay hydrated!"

        return "I'm here to assist you with personalized fitness advice! Let me know what you'd like help with."

    # Get user input and provide a dynamic response
    if prompt := st.chat_input("Ask me anything about your fitness plan!"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("fitness instructor"):
            # Generate and show the response based on user input
            reply = generate_response(prompt)
            st.write(reply)
            st.session_state.messages.append({"role": "fitness instructor", "content": reply})
