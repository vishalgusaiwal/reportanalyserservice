# test_analyzer.py

from haystack_engine.analyser import analyze_pdf_report
from io import BytesIO

if __name__ == "__main__":
    file_path = "C:/Users/visha/JavaProject/reportanalyserservice/app/sample.pdf"  # Path to your test PDF
    try:
        # with open(file_path, "rb") as file:
        #     bytestream = BytesIO(file.read())

        summary = analyze_pdf_report(file_path)
        print("\n--- Medical Report Summary ---\n")
        print(summary)
    except Exception as e:
        print(f"Error: {e}")
