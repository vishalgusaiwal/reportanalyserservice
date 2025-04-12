import json
from storage.downloader import AzureBlobDownloader
from haystack_engine.analyser import analyze_pdf_report
from utils.formatter import build_email_text
from kafkaService.consumer import KafkaReportConsumer
from kafkaService.producer import KafkaReportProducer
# import threading
# from concurrent.futures import ThreadPoolExecutor

# executor = ThreadPoolExecutor(max_workers=3)  # Adjust based on load

def process_report(message: dict):
    """
    Handles the full processing pipeline for a given report.
    """
    try:
        print("in process_report")
        report_url = message["reportUrl"]
        patient_id = message["email"]
        print(f"🔄 Processing report for patient: {patient_id}")

        # 1. Download PDF
        downloadPath = "C:/Users/visha/JavaProject/reportanalyserservice/app"
        downloader = AzureBlobDownloader()
        local_pdf_path = downloader.download_blob(report_url,download_path=downloadPath)
        print(f"📥 Downloaded report to: {local_pdf_path}")
        # 2. Analyze PDF
        summary = analyze_pdf_report(local_pdf_path)

        # 3. Format email content
        email_text = build_email_text(patient_id, summary)

        # 4. Push to Kafka (email-output-topic)
        output_payload = {
            "email": patient_id,
            "body": email_text,#"dummy body",
            "subject": "Your Medical Report Analysis"
        }
        producer = KafkaReportProducer(
            topic="email-output-topic",
            bootstrap_servers="kafka-27ebcf53-ee-9d0c.k.aivencloud.com:23051"
        )
        producer.produce_email_payload(output_payload)

        print(f"✅ Completed processing for {patient_id}\n")

    except Exception as e:
        print(f"❌ Error while processing report: {e}")

# def threaded_callback(message: dict):
#     executor.submit(process_report, message)

if __name__ == "__main__":
    print("🚀 Agent started. Waiting for Kafka messages...\n")
    consumer = KafkaReportConsumer(
        topic="report-topic",
        group_id="medical-report-group2",
        bootstrap_servers=["kafka-27ebcf53-ee-9d0c.k.aivencloud.com:23051"]
    )
    consumer.listen(process_report)