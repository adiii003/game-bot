import streamlit as st
from pymongo import MongoClient
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# MongoDB Details (Replace with your actual connection details)
MONGO_URI = "mongodb://localhost:27017"  # Update with your MongoDB URI
DB_NAME = "games_db"
COLLECTION_NAME = "games"

# Groq API Key
GROQ_API_KEY = "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"

# Groq LLM
llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="gemma2-9b-it")

# Streamlit UI Configuration
st.set_page_config(page_title="Game Chatbot", page_icon="🎮", layout="wide")

st.markdown("""
    <style>
        .stTextInput>label {
            font-size: 24px;  /* Adjust the font size here */
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        .custom-header {
            font-size: 35px;  /* Change the font size here */
            font-weight: bold;
            color: #333333;
        }
    </style>
""", unsafe_allow_html=True)

# Display the custom header before the input box
st.markdown('<p class="custom-header">Ask me anything about games:</p>', unsafe_allow_html=True)

# Initialize session state for conversation history and input
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'input' not in st.session_state:
    st.session_state.input = ""  # Initialize input state to an empty string

# MongoDB Client Connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def get_game_info(game_name):
    """Fetches game information from MongoDB."""
    result = collection.find_one({"title": {"$regex": game_name, "$options": "i"}})
    if result:
        return f"**{result.get('title')}**\n" \
               f"**Developer:** {result.get('developer')}\n" \
               f"**Publisher:** {result.get('publisher')}\n" \
               f"**Genres:** {', '.join(result.get('genres', []))}\n" \
               f"**Description:** {result.get('description')[:150]}..."  # Shorten description
    else:
        return f"No information found for game: {game_name}"

def generate_response(user_input):
    """Generates a response using the LLM."""
    prompt = PromptTemplate(
        input_variables=["game_info"],
        template="Provide a concise and informative response about the game based on the following information:\n\n{game_info}"
    )

    llm_chain = LLMChain(prompt=prompt, llm=llm)
    game_info = get_game_info(user_input)
    response = llm_chain.run(game_info=game_info)
    return response

# Display chat history and user input
for message in st.session_state.messages:
    col1, col2 = st.columns([1, 4])  # Layout for alignment

    with col1:
        if message["role"] == "user":
            st.empty()  # Placeholder for alignment
        else:
            st.write("")  # Placeholder for bot alignment

    with col2:
        # Define common style
        user_style = """
            background-color: #E8E8E8; 
            padding: 10px; 
            border-radius: 5px; 
            margin-bottom: 10px; 
            box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
        """
        bot_style = """
            background-color: #DCF8C6; 
            padding: 10px; 
            border-radius: 5px; 
            margin-bottom: 10px; 
            box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
        """
        # Apply style based on the role
        if message["role"] == "user":
            st.markdown(
                f"<div style='{user_style}'>{message['content']}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div style='{bot_style}'>{message['content']}</div>",
                unsafe_allow_html=True,
            )

# Callback function to process user input and clear input field
def process_input():
    user_input = st.session_state.input  # Get user input from session state
    
    if user_input:  # Process only if there's input
        # Add user message to session state
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Generate bot response
        response = generate_response(user_input)

        # Add bot response to session state
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Clear the input field
        st.session_state.input = ""  # Reset the input field

# Input box with callback
user_input =st.text_input(
    "", 
    value=st.session_state.input, 
    key="input", 
    on_change=process_input  # Trigger the callback when Enter is pressed
)

# Add some visual enhancements
st.sidebar.title("🎮 Game Chatbot")
st.sidebar.info("Powered by Groq LLM")
