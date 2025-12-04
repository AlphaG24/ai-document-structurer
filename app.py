import streamlit as st
import pandas as pd
import json
from pypdf import PdfReader
import google.generativeai as genai
import io

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="AI Document Structurer", layout="wide")

# --- HELPER FUNCTIONS ---
def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def process_with_gemini(text_content, api_key, model_name):
    # Configure Gemini with the key
    genai.configure(api_key=api_key)
    
    try:
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        You are an expert Data Extraction AI. Convert this text into a JSON list.
        DOCUMENT TEXT: {text_content}
        
        RULES:
        1. Output a JSON list of objects with fields: "Key", "Value", "Comments".
        2. "Key": Infer from context (e.g., "Date of Birth"). No pre-defined keys.
        3. "Value": The extracted data.
        4. "Comments": Context or original phrasing.
        5. Capture 100% of data.
        
        IMPORTANT: Return ONLY valid JSON. Do not use markdown code blocks. Just the raw JSON string.
        """
        
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        st.error(f"Error with model {model_name}: {e}")
        return None

# --- MAIN APP LAYOUT ---
st.title("📄 AI-Powered Document Structuring Agent")
st.markdown("**Internship Assignment Submission** | Candidate: Raghav")

# --- API KEY HANDLING (AUTO-FETCH FROM SECRETS) ---
api_key = None

# 1. Try to fetch from secrets.toml
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.sidebar.success("✅ API Key loaded from secrets.toml")
except FileNotFoundError:
    # This happens if the .streamlit folder is missing (safe to ignore)
    pass
except Exception as e:
    # Any other error with secrets
    pass

# 2. If secrets failed, ask in sidebar
if not api_key:
    api_key = st.sidebar.text_input("Enter Google Gemini API Key", type="password")

# --- DYNAMIC MODEL SELECTOR ---
selected_model_name = None
if api_key:
    try:
        genai.configure(api_key=api_key)
        # Get list of models available to THIS key
        model_list = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                model_list.append(m.name)
        
        if model_list:
            model_list.sort()
            # Default to Flash if available, otherwise first item
            default_index = 0
            for i, m in enumerate(model_list):
                if "flash" in m:
                    default_index = i
                    break
            
            selected_model_name = st.sidebar.selectbox("Select Model", model_list, index=default_index)
        else:
            st.sidebar.error("Key works, but no models found.")
            
    except Exception as e:
        st.sidebar.error(f"Invalid Key or Connection Error: {e}")

# --- UPLOAD & PROCESS ---
uploaded_file = st.file_uploader("Upload PDF Document", type="pdf")

if uploaded_file and st.button("Process Document"):
    if not api_key:
        st.warning("Please enter your API Key first.")
    elif not selected_model_name:
        st.warning("Model loading... please wait a moment.")
    else:
        with st.spinner(f"Processing with {selected_model_name}..."):
            raw_text = extract_text_from_pdf(uploaded_file)
            json_response = process_with_gemini(raw_text, api_key, selected_model_name)
            
            if json_response:
                try:
                    # Clean markdown if present
                    clean_json = json_response.replace("```json", "").replace("```", "").strip()
                    data = json.loads(clean_json)
                    
                    # Normalize list/dict
                    if isinstance(data, dict):
                        for k, v in data.items():
                            if isinstance(v, list):
                                data = v
                                break
                    
                    # Create DataFrame
                    df = pd.DataFrame(data)
                    if not df.empty:
                        df.insert(0, '#', range(1, 1 + len(df)))
                    
                    st.success("Processing Complete!")
                    st.dataframe(df, use_container_width=True)
                    
                    # Excel Download
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False)
                    st.download_button("📥 Download Output.xlsx", output.getvalue(), "Output.xlsx")
                    
                except Exception as e:
                    st.error("Failed to parse the AI response.")
                    st.code(json_response)