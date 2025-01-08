# pip install streamlit streamlit_drawable_canvas

import streamlit as st
from streamlit_drawable_canvas import st_canvas
import google.generativeai as genai 
import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Google QuickDraw Clone", page_icon="🎨"
)

st.title("QuickDraw Clone powered by Gemini")
st.markdown(
"""
Welcome to QuickDraw!
Unleash your inner artist and challenge our AI to guess your doodles. Draw, test, and see if our AI can keep up with your creativity. Let the fun begin! 
"""
)

key = st.secrets["gemini_api_key"]
genai.configure(api_key=key)
model1 = genai.GenerativeModel('gemini-1.5-flash',system_instruction="""Each time you are asked to generate a word, generate a unique word each time that is easy to draw and understand during a game of pictionary. Make sure not to use words generated previously. Do not generate sun.""")
# Setting our parameters
custom_config = genai.types.GenerationConfig(temperature=2)
chat = model1.start_chat(history=[])
#prompt = """Generate a list of 15 words that are simple to draw and #easy to guess. Make sure these words are in a list in python #withoutthe need for markdown or assigning to any variable. Produce #onlythis output and nothing else."""
# Passing our custom parameters to the generate_content method
#list_of_words = chat.send_message(prompt, generation_config=custom_config)

if st.button("Generate a word"):
    # Create a prompt that includes previously generated words
    previously_generated = ", ".join(st.session_state['word'])
    prompt = f"""Generate a unique word that is easy to draw and understand during a game of pictionary. Do not generate any of these words: {previously_generated if previously_generated else "none"}.
    The word should be in lowercase only.
    """
    word = chat.send_message(prompt)
    if 'word' not in st.session_state:
        st.session_state['word'] = []  # Initialize as an empty list
    st.session_state['word'].append(word.text)
    #st.subheader(f"Your word is: {st.session_state['word'][-1]}")
    #st.write(st.session_state['word'][0])

# Display the current word if the list is not empty
if 'word' in st.session_state and st.session_state['word']:
    st.subheader(f"Your word is: {st.session_state['word'][-1]}")
drawing_mode = st.sidebar.selectbox(
    "Drawing tool:",
    ("freedraw", "line", "rect", "circle", "transform", "polygon", "point"),
)
stroke_width = st.sidebar.slider("Stroke width: ", 1, 25, 3)
if drawing_mode == "point":
    point_display_radius = st.sidebar.slider("Point display radius: ", 1, 25, 3)
stroke_color = st.sidebar.color_picker("Stroke color hex: ")
bg_color = st.sidebar.color_picker("Background color hex: ", "#fff")
# Canvas for drawing
canvas_result = st_canvas(
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    update_streamlit=True,
    width=480,
    drawing_mode=drawing_mode,
    point_display_radius=point_display_radius if drawing_mode == "point" else 0,
    key="full_app",
)

if "word" not in st.session_state:
        st.session_state["word"] = []
model2 = genai.GenerativeModel('gemini-1.5-flash')
# Setting our parameters
custom_config = genai.types.GenerationConfig(temperature=0.5)
chat = model2.start_chat(history=[])     
if st.button("Guess"):
    if canvas_result.image_data is not None:
        # Convert to PIL Image
        image = Image.fromarray((canvas_result.image_data).astype("uint8"),         "RGBA")
        prompt=f"""Guess the drawing. Only generate the word and nothing else."""
        response = model2.generate_content([image, prompt],generation_config=custom_config)
        # Show the image in Streamlit
        #st.image(image, caption="Your Drawing")
        
        with st.chat_message("assistant"):
            st.write(response.text.lower())
            #st.write(st.session_state['word'][-1])
        if st.session_state['word'][-1].strip().lower() == response.text.strip().lower():
            st.write("Model has guessed correctly!!")
        else:
            st.write("The model has failed to guess correctly!")

    