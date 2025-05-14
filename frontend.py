import streamlit as st
import requests

def add_custom_css():
    st.markdown("""
    <style>
        .body {
            background-image: url('images.jpeg');
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }
        .stButton>button {                
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
            padding: 15px 40px;
            font-size: 18px;
            display: block;
            margin: 0 auto;
        }
        .stTextArea>div>textarea {
            border: 2px solid #4CAF50;
            border-radius: 8px;
            padding: 10px;
            font-size: 18px;
        }
        .title h1 {
            text-align: center;
            font-family: 'Arial Black', sans-serif;
            text-transform: uppercase;
            font-size: 48px;
            color: #4CAF50;
        }
    """, unsafe_allow_html=True)

add_custom_css()

st.markdown('<div class="title"><h1>Welcome to TaskSync</h1></div>', unsafe_allow_html=True)

# Input prompt with a placeholder
user_input = st.text_area("", placeholder="What's your next prompt...", height=150, key="input")

# Placeholder for output
output_placeholder = st.empty()

if st.button("Submit"):
    api_url = "http://localhost:5000/api/receive"
    
    # Data to be sent to the Flask API
    user_data = {
        'text': user_input  # Make sure the key matches the backend expectations
    }
    
    # Log the data being sent to the API for debugging purposes
    st.write("Your final team :", user_data)
    
    # Make POST request to send data
    try:
        response = requests.post(api_url, json=user_data)
        if response.status_code == 201:
            # Extract clean text from the response JSON
            response_data = response.json()  # Convert response to JSON
            text_value = response_data.get('text', '')  # Get the value associated with 'text'
            st.success("Data submitted successfully!")
            output_placeholder.markdown(f'<div class="output-box">{text_value}</div>', unsafe_allow_html=True)
        else:
            st.error(f"Failed to submit data: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
    
    # Clear the input box
        # st.session_state.input = ""