# app/utils/formatter.py

def build_email_text(patient_email_id: str, summary: dict) -> str:
    """
    Convert analysis summary into a plain-text email message.
    """
    try:
        print(summary)
        key_points = "\n- ".join(summary.get("key_points", []))
        highlights = "\n- ".join(summary.get("highlights", []))
        precautions = "\n- ".join(summary.get("precautions", []))
        # print("Key points----------------------\n",key_points)
        # print("highlights----------------------\n",highlights)
        # print("precautions----------------------\n",precautions)
        email_text = f"""
        Dear Patient ({patient_email_id}),

        We have completed an AI-based analysis of your medical report. Please find the insights below:

        🩺 Key Medical Points:
        - {key_points}

        ✨ Highlights:
        - {highlights}

        ⚠️ Precautions & Recommendations:
        - {precautions}

        Please consult with your healthcare provider for detailed review and guidance.

        Regards,
        AI Medical Assistant
        """
        print(email_text)
        return email_text.strip()
    except Exception as e:
        print(f"Error in building email text: {e}")
        return "Dear Patient, we encountered an error while processing your report. Please contact support."
