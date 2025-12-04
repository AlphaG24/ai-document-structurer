# AI-Powered Document Structuring & Data Extraction

## Overview
This project is a solution for the AI Agent Development internship assignment. It is an AI-powered tool designed to transform unstructured PDF documents into structured Excel datasets without using pre-defined keys.

## Features
- **Dynamic Key Extraction:** Uses **Google Gemini 2.0 Flash** to infer keys based on context, ensuring no information is lost.
- **Context Preservation:** Captures original wording and context in a dedicated "Comments" column.
- **100% Data Capture:** Designed to extract every logical data point, including demographics, career history, and certifications.
- **Live Interface:** Built with Streamlit for real-time interaction and immediate visualization.
- **Secure Deployment:** Uses Streamlit Secrets management for secure API key handling.

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- A **Google Gemini API Key**

### 2. Installation
Clone the repository and install dependencies:

```bash
git clone https://github.com/AlphaG24/ai-document-structurer.git
cd ai-document-structurer
pip install -r requirements.txt

