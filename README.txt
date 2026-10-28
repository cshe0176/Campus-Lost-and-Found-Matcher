COMP9001 FINAL PROJECT - CAMPUS LOST & FOUND MATCHER
====================================================

WHAT IT DOES
A campus lost-property tool. Students can add lost or found item reports,
compare possible matches using an explainable scoring system, view old
reports, and mark a recovered item as resolved. All records remain local.

RECOMMENDED WAY TO RUN IN ED (RELIABLE / TEXT VERSION)
1. Use Python 3 (no extra packages).
2. Run: python3 main.py   (or python main.py)
3. Choose 3, then report ID 1, to try the included sample records.
4. Menu options also allow adding new reports or resolving an existing one.

OPTIONAL VISUAL DEMONSTRATION ON A LAPTOP
1. Run: python3 web_app.py   (or python web_app.py)
2. Open http://127.0.0.1:8765 in any modern browser on the SAME computer.
3. Choose report #1 and click 'Find matches'. The top suggestion has
   a similarity score of 100/100; the next has 65/100.
4. Use Ctrl+C in the original terminal to stop the local web server.
The visual mode may not work inside Ed. Use main.py in Ed. The visual
interface is OPTIONAL, but it calls the Python functions in main.py and
uses the same data file. No external website or third-party library is
required. If you plan to demonstrate the visual interface, submit its
Python file as well and disclose any AI help you actually used.

FILES
main.py             Core program and the terminal interface (run this in Ed)
web_app.py          Optional local browser interface (run on a laptop)
reports.json        Synthetic example reports so a demo works immediately
test_main.py        Tests for core logic
test_web_app.py      Tests for the optional local browser interface
README.txt          This document

MATCH ALGORITHM
Only opposite report types can match (lost versus found).
The item category must be the same. Matching attributes receive:
  Category 40 points; exact colour 25; exact location 15;
  shared useful description words: up to 20.
Suggestions are shown when they score at least 50/100.
Scores are rule-based similarities, not probabilities or proof of ownership.
The broad 'Other' category requires a useful common description word.
Solved reports are no longer recommended. Spelling, synonyms and missing
details can affect matching; the owner must verify the item in person.

STORAGE / PRIVACY
reports.json is stored in the same folder as main.py. Adding or resolving
an item changes this file. To get a fresh start, move or rename reports.json.
The software will then create an empty dataset when you add your first item.
The sample dataset is fictitious. Do not use private student information.

TECHNICAL CONCEPTS
- Week 7: ItemReport class; methods for displaying and converting reports.
- Week 8: conditional flow, break/continue, exception handling.
- Week 9: JSON file reading/writing and handling missing/corrupt files.
- Week 10: automated tests (unittest) for normal, invalid and edge cases.
- Core fundamentals: functions, loops, lists, dictionaries, strings, sorting.
The user interface is not required to obtain advanced concept marks;
real matching and data handling are implemented in main.py.

TESTING (OPTIONAL)
From this folder run:
    python3 -m unittest discover -v
Tests use a temporary data file and should not change demo reports.json.

AI / ACADEMIC INTEGRITY
This project package was developed with substantial ChatGPT assistance.
Review the unit's rules and disclose AI use accurately. The student should
understand, adapt, test and explain the code and describe their own input.
The browser presentation in particular was AI-assisted. Do not imply it
was fully hand-written. The poster is illustrative only; actual browser
screenshots and real executable Python files are also provided.

TROUBLESHOOTING
- 'python not found': try python3 or check your Python 3 installation.
- 'Address already in use': stop an existing web_app.py session, or run
   python3 web_app.py --port 8766 and open http://127.0.0.1:8766
- Browser not opening: copy the displayed http://127.0.0.1... address into
  your browser. Do not open this address on another device.
- Corrupt reports.json: the terminal program gives an error without
  silently replacing the data. Move/backup the file before continuing.
