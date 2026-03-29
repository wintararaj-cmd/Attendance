import google.generativeai as genai
import os
import pandas as pd
import json
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("ai_service")

class AIService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key and "your_gemini_api_key" not in self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.enabled = True
        else:
            self.enabled = False
            logger.info("AI Service disabled: No valid GEMINI_API_KEY found in .env")

    def get_excel_layout(self, df: pd.DataFrame):
        """
        Analyze the first 20 rows of the dataframe to detect the attendance report layout.
        Returns a JSON object with col/row indices.
        """
        if not self.enabled:
            return None

        try:
            # Extract first 20 rows and 20 columns to keep it lightweight
            sample = df.iloc[:20, :20].fillna("").astype(str).values.tolist()
            sample_text = "\n".join([", ".join(row) for row in sample])

            prompt = f"""
            Analyze this attendance report Excel structure (first 20 rows):
            {sample_text}

            Identify and return ONLY a JSON object with these keys:
            - day_1_column_index: The column index where attendance day "01" or "1" is located.
            - employee_code_column_index: The column where employee IDs are (usually 0).
            - month_year_text: The full text containing the month and year (e.g. "Month of December, 2025").
            - label_column_index: The column where labels like "In Time", "Out Time", "Status" are usually located (usually 0).
            - rows_per_employee: How many rows represent one employee's daily details (In, Out, etc).
            - status_codes: A map of discovered status codes to meaning (e.g. AA -> absent, PP -> present).

            Return ONLY the valid JSON, no other text.
            """

            response = self.model.generate_content(prompt)
            result = response.text.strip()
            # Clean up potential markdown code blocks
            if result.startswith("```json"):
                result = result[7:-3].strip()
            elif result.startswith("```"):
                result = result[3:-3].strip()

            return json.loads(result)
        except Exception as e:
            logger.error(f"AI Excel analysis failed: {e}")
            return None

    def map_unknown_status(self, status_code: str):
        """Help map a status value like 'PPl' or 'WW' to 'present' or 'absent' if the local logic is unsure."""
        if not self.enabled:
            return None
            
        try:
            prompt = f"In an attendance report, what does the status code '{status_code}' mean? Respond with just one word: 'present' or 'absent'."
            response = self.model.generate_content(prompt)
            meaning = response.text.strip().lower()
            if 'present' in meaning: return 'present'
            if 'absent' in meaning: return 'absent'
            return None
        except:
            return None

ai_service = AIService()
