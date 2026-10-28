"""COMP9001 Final Project: Campus Lost & Found Matcher.

Run with: python3 main.py
Uses only Python's standard library.
"""

import json
import re
from pathlib import Path


DATA_FILE = Path(__file__).with_name("reports.json")
CATEGORIES = [
    "Bag", "Bottle", "Electronics", "Keys", "Wallet", "Clothing",
    "Umbrella", "Cards", "Other"
]
MINIMUM_MATCH_SCORE = 50
COMMON_WORDS = {
    "a", "an", "and", "the", "my", "your", "with", "in", "at", "near",
    "on", "of", "to", "is", "was", "it", "this", "that", "item",
    "lost", "found", "some", "has", "have"
}


class ItemReport:
    """Store the information for one lost or found item."""

    def __init__(self, report_id, report_type, category, colour,
                 location, description, status="active"):
        self.report_id = report_id
        self.report_type = report_type
        self.category = category
        self.colour = colour
        self.location = location
        self.description = description
        self.status = status

    def to_dictionary(self):
        """Convert an object to data that JSON can save."""
        return {
            "id": self.report_id,
            "type": self.report_type,
            "category": self.category,
            "colour": self.colour,
            "location": self.location,
            "description": self.description,
            "status": self.status
        }

    def display(self):
        print(f"Report ID: {self.report_id}")
        print(f"Type: {self.report_type.title()}")
        print(f"Status: {self.status.title()}")
        print(f"Category: {self.category}")
        print(f"Colour: {self.colour}")
        print(f"Location: {self.location}")
        print(f"Description: {self.description}")


def load_reports():
    """Read past reports, or start with an empty list on the first run."""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            saved_data = json.load(file)
    except FileNotFoundError:
        return []
    except (json.JSONDecodeError, OSError) as error:
        raise ValueError(f"Cannot read {DATA_FILE.name}: {error}") from error

    if not isinstance(saved_data, list):
        raise ValueError("Saved reports have the wrong format (expected a list).")

    reports = []
    seen_ids = set()
    for entry in saved_data:
        try:
            report = ItemReport(
                entry["id"], entry["type"], entry["category"],
                entry["colour"], entry["location"], entry["description"],
                entry["status"]
            )
            if (not isinstance(report.report_id, int)
                    or isinstance(report.report_id, bool)
                    or report.report_id < 1
                    or report.report_id in seen_ids
                    or report.report_type not in ("lost", "found")
                    or report.status not in ("active", "resolved")
                    or report.category not in CATEGORIES
                    or any(not isinstance(value, str) or not value.strip()
                           for value in (report.colour, report.location,
                                         report.description))):
                raise ValueError("Invalid report information")
            seen_ids.add(report.report_id)
            reports.append(report)
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("The saved reports contain invalid data.") from error

    return reports


def save_reports(reports):
    """Save reports as readable JSON; this file is created automatically."""
    data = [report.to_dictionary() for report in reports]
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def next_report_id(reports):
    """Use a unique ID even if reports are resolved."""
    return max((report.report_id for report in reports), default=0) + 1


def required_input(prompt):
    """Ask again if the user enters an empty answer."""
    while True:
        answer = input(prompt).strip()
        if answer:
            return answer
        print("Please enter a value; it cannot be empty.")


def select_category():
    print("\nChoose a category:")
    for number, category in enumerate(CATEGORIES, start=1):
        print(f"{number}. {category}")

    while True:
        choice = input(f"Category (1-{len(CATEGORIES)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(CATEGORIES):
            return CATEGORIES[int(choice) - 1]
        print("Please select a number from the category list.")


def add_report(reports, report_type):
    """Create and save a lost or found report."""
    print(f"\n--- Report a {report_type.title()} Item ---")
    category = select_category()
    colour = required_input("Colour: ")
    location = required_input("Campus location: ")
    description = required_input("Short description: ")

    report = ItemReport(next_report_id(reports), report_type,
                        category, colour, location, description)
    reports.append(report)
    try:
        save_reports(reports)
    except OSError as error:
        reports.pop()  # Do not pretend a report was saved if writing failed.
        print(f"Unable to save this report: {error}")
        return

    print(f"\nSaved! Your {report_type} report ID is {report.report_id}.")


def view_reports(reports):
    print("\n--- All Reports ---")
    if not reports:
        print("No reports have been recorded yet.")
        return

    for report in reports:
        print("\n" + "-" * 34)
        report.display()
    print("-" * 34)


def find_report_by_id(reports, report_id):
    for report in reports:
        if report.report_id == report_id:
            return report
    return None


def ask_report_id():
    try:
        report_id = int(input("Enter a report ID: ").strip())
        if report_id < 1:
            raise ValueError
        return report_id
    except ValueError:
        print("Invalid ID. Please enter a positive whole number.")
        return None


def normalise(text):
    """Ignore differences in letter case and extra spaces."""
    return " ".join(text.casefold().split())


def description_words(text):
    """Keep informative words instead of punctuation/common filler words."""
    words = re.findall(r"[a-z0-9]+", text.casefold())
    return set(word for word in words if word not in COMMON_WORDS)


def match_breakdown(first, second):
    """Return (score, reasons) explaining how two items compare.

    This is a rule-based similarity score, NOT a probability or AI model.
    Only reports from the same category are compared. For the very broad
    'Other' category we also require a meaningful shared description word.
    """
    if normalise(first.category) != normalise(second.category):
        return 0, []

    common = description_words(first.description) & description_words(second.description)
    # For "Other", a shared colour word alone is too vague to suggest a match.
    meaningful_common = common - description_words(first.colour) - description_words(second.colour)
    if first.category == "Other" and not meaningful_common:
        return 0, []

    score = 40
    reasons = ["Same category (+40)"]

    if normalise(first.colour) == normalise(second.colour):
        score += 25
        reasons.append("Same colour (+25)")

    if normalise(first.location) == normalise(second.location):
        score += 15
        reasons.append("Same location (+15)")

    description_points = min(len(common) * 5, 20)
    if description_points:
        score += description_points
        reasons.append(f"Shared description words (+{description_points})")

    return score, reasons


def calculate_match_score(first, second):
    """Return a score from 0 to 100; useful for automated testing."""
    score, _ = match_breakdown(first, second)
    return score


def find_matches(reports):
    print("\n--- Find Possible Matches ---")
    active_reports = [report for report in reports if report.status == "active"]
    if not active_reports:
        print("No active reports are available.")
        return

    print("Choose one of these active reports:")
    for report in active_reports:
        print(f"  {report.report_id}: {report.report_type.title()} - "
              f"{report.colour} {report.category} ({report.location})")

    selected_id = ask_report_id()
    if selected_id is None:
        return

    selected = find_report_by_id(reports, selected_id)
    if selected is None or selected.status != "active":
        print("That active report does not exist.")
        return

    results = []
    for candidate in active_reports:
        # Lost reports can only match found reports (and vice versa).
        if candidate.report_type == selected.report_type:
            continue
        score, reasons = match_breakdown(selected, candidate)
        if score >= MINIMUM_MATCH_SCORE:
            results.append((score, candidate, reasons))

    # Highest similarity first; ID breaks ties in a predictable order.
    results.sort(key=lambda result: (-result[0], result[1].report_id))

    if not results:
        print("\nNo close matches yet. You can check again after more reports are added.")
        return

    print("\nPossible matches (highest similarity first):")
    print("Scores are comparison points, not probabilities of a true match.")
    for position, (score, candidate, reasons) in enumerate(results, start=1):
        print(f"\nMatch {position} | Similarity score: {score}/100")
        print("Why it matched: " + "; ".join(reasons))
        candidate.display()
        print("-" * 34)


def mark_resolved(reports):
    """Keep old reports for the record but hide them from matching."""
    print("\n--- Mark a Report as Resolved ---")
    report_id = ask_report_id()
    if report_id is None:
        return

    report = find_report_by_id(reports, report_id)
    if report is None:
        print("Report not found.")
    elif report.status == "resolved":
        print("This report is already marked as resolved.")
    else:
        report.status = "resolved"
        try:
            save_reports(reports)
        except OSError as error:
            report.status = "active"
            print(f"Unable to save this change: {error}")
            return
        print(f"Report {report_id} is now resolved and will not appear in matches.")


def display_menu():
    print("\n" + "=" * 43)
    print("       CAMPUS LOST & FOUND MATCHER")
    print("=" * 43)
    print("1. Report a lost item")
    print("2. Report a found item")
    print("3. Find possible matches")
    print("4. View all reports")
    print("5. Mark a report as resolved")
    print("6. Exit")


def main():
    try:
        reports = load_reports()
    except ValueError as error:
        print(f"Data error: {error}")
        print("Your existing data file has been left unchanged.")
        return

    while True:
        display_menu()
        choice = input("Choose an option (1-6): ").strip()
        if choice == "1":
            add_report(reports, "lost")
        elif choice == "2":
            add_report(reports, "found")
        elif choice == "3":
            find_matches(reports)
        elif choice == "4":
            view_reports(reports)
        elif choice == "5":
            mark_resolved(reports)
        elif choice == "6":
            print("\nThank you for using Campus Lost & Found Matcher!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 6.")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nProgram closed. Previously saved reports are safe.")
