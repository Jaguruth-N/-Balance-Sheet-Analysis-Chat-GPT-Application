import google.generativeai as genai
import os

# --- IMPORTANT ---
# PASTE YOUR GOOGLE API KEY DIRECTLY HERE FOR THIS TEST
YOUR_API_KEY = "AIzaSyCX16UrexlPuF8KK8P5P58p0jhWL24l_WI"

try:
    genai.configure(api_key=YOUR_API_KEY)

    print("--- Finding available models for your API key ---")
    for m in genai.list_models():
      # Check if the model supports the 'generateContent' method
      if 'generateContent' in m.supported_generation_methods:
        print(f"Model found: {m.name}")
    print("-------------------------------------------------")
    print("\nSUCCESS: Choose one of the models listed above.")

except Exception as e:
    print(f"An error occurred: {e}")
    print("Please ensure your API key is pasted correctly in the script.")