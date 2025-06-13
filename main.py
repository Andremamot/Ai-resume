import streamlit as st
import PyPDF2
import io
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title= "Resume AI", page_icon= "📃", layout="centered")

st.title("Resume AI")
st.markdown("Upload your file for resume ")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

upload_file = st.file_uploader("Upload Your File (PDF or TXT)", type= ["pdf", "txt"])
job_role = st.text_input ("Enter your target resume (optional)")

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_file(upload_file):
    if upload_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(upload_file.read()))
    return upload_file.read().decode ("utf-8")

analyze = st.button ("analyze Resume")

if analyze and upload_file :
    try:
        file_content = extract_text_from_file(upload_file)

        if not file_content.strip():
            st.error ("format does not match")
            st.stop
        
        prompt = f""" Please analyze this resume for constructive feedback.

        Focus the analysis of this resume on aspects such as:
        1. the content of the resume, and the clarity and impact of the resume
        2. the description matches your experience
        3.and specific to the target resume {job_role if job_role else 'your target'}

        resume content :
        {file_content}

        create a resume that is structured, clear and also fits the topic of the resume."""
        
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a reviewer who has experience in reading and summarizing resumes and has experience in the field."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=100
        )

        st.markdown('#Result')
        st.markdown(response.choices[0].message.content)

    except Exception as e:
        st.error(f"An error occured: {str(e)}")