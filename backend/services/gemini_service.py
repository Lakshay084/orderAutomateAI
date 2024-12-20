import os
import requests
from .auth import get_access_token
from dotenv import load_dotenv

load_dotenv(dotenv_path="/Users/lakshaynagar/Desktop/WEB DEV/orderAutomateAI/.env")

class GeminiClient:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        print(f"Loaded API Key: {self.api_key}")
        self.model = "gemini-1.5-flash"
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    def generate_email(self, supplier_name, purpose, product_name, price, rating):
        # Prepare prompt based on purpose
        if purpose == "negotiation":
            prompt_text = f"""
            Write a professional email to {supplier_name} to negotiate a better price for {product_name}.
            The current price is {price}, and their rating is {rating}. Suggest a 10% discount based on market analysis.
            """
        elif purpose == "restocking":
            prompt_text = f"""
            Write a professional email to {supplier_name} to request restocking of {product_name}.
            Their available quantity is critically low, and immediate action is needed to prevent stockouts.
            """
        else:
            prompt_text = f"""
            Write a follow-up email to {supplier_name} praising their performance.
            Mention their high rating of {rating} and express interest in further collaboration.
            """

        # Debugging: Log the prompt
        print("Prompt Text:", prompt_text)
        token = get_access_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt_text}]
                }
            ]
        }

        # Debugging: Log the payload
        print("Payload Sent to Gemini API:", payload)

        response = requests.post(self.api_url, headers=headers, json=payload)

        # Debugging: Log the response
        print("Response Status Code:", response.status_code)
        print("Response Text:", response.text)

        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            error_message = response.json().get("error", {}).get("message", "Unknown error")
            raise Exception(f"Gemini API Error: {response.status_code} - {error_message}")

# For testing purposes
if __name__ == "__main__":
    client = GeminiClient()
    try:
        response = client.generate_email(
            supplier_name="Supplier_3",
            purpose="negotiation",
            product_name="Wheat",
            price="368",
            rating="3.4"
        )
        print("Generated Email:", response)
    except Exception as e:
        print("Error:", e)
