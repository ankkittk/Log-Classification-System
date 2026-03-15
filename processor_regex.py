import re

regex_patterns = {
        r"User User\d+ logged (in|out).": "User Action",
        r"Backup (started|ended) at .*": "System Notification",
        r"Backup completed successfully.": "System Notification",
        r"System updated to version .*": "System Notification",
        r"File .* uploaded successfully by user .*": "System Notification",
        r"Disk cleanup completed successfully.": "System Notification",
        r"System reboot initiated by user .*": "System Notification",
        r"Account with ID .* created by .*": "User Action"
    }

def classify_with_regex(log_message, regex_patterns = regex_patterns):
    for pattern, label in regex_patterns.items():
        if re.search(pattern, log_message, re.IGNORECASE):
            return label
    return "Unclassified"

if __name__ == "__main__":
    #add 7 test cases to validate the regex patterns
    test_cases = [
        "User User123 logged in.",
        "User User456 logged out.",
        "Backup started at 2024-06-01 10:00:00.",
        "Backup ended at 2024-06-01 12:00:00.",
        "Backup completed successfully.",
        "System updated to version 1.2.3.",
        "File report.pdf uploaded successfully by user User789."
    ]
    for test in test_cases:
        classification = classify_with_regex(test)
        print(f"Log Message: '{test}' => Classification: '{classification}'")
    