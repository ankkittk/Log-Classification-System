from processor_regex import classify_with_regex
import numpy as np

rare_sources = np.load("rare_sources.npy", allow_pickle=True)

def classify(logs):
    for src, log in logs:
        print(classify_log(src, log))

def classify_log(src, log_message):
    if src in rare_sources:
        pass #LLM
    else:
        label = classify_with_regex(log_message)
        if label == "Unclassified":
            pass #BERT
        return label

if __name__ == "__main__":
    logs = [
        ("ModernCRM", "IP 192.168.133.114 blocked due to potential attack"),
        ("BillingSystem", "User 12345 logged in."),
        ("AnalyticsEngine", "File data_6957.csv uploaded successfully by user User265."),
        ("AnalyticsEngine", "Backup completed successfully."),
        ("ModernHR", "GET /v2/54fadb412c4e40cdbaed9335e4c35a9e/servers/detail HTTP/1.1 RCODE  200 len: 1583 time: 0.1878400"),
        ("ModernHR", "Admin access escalation detected for user 9429"),
        ("LegacyCRM", "Case escalation for ticket ID 7324 failed because the assigned support agent is no longer active."),
        ("LegacyCRM", "Invoice generation process aborted for order ID 8910 due to invalid tax calculation module."),
        ("LegacyCRM", "The 'BulkEmailSender' feature is no longer supported. Use 'EmailCampaignManager' for improved functionality."),
        ("LegacyCRM", " The 'ReportGenerator' module will be retired in version 4.0. Please migrate to the 'AdvancedAnalyticsSuite' by Dec 2025")
    ]

    classify(logs)