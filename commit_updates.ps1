# commit_updates.ps1
# This script stages, commits, and pushes the recent performance enhancements.
# Run it from the repository root (d:\AUDIO SERIES AGENT).

# Stage changed files and new files
git add translator.py audio_processor.py scraper.py config.py utils.py app.py

# Commit with a descriptive message
git commit -m "Add ETA timestamp display to Streamlit UI and missing config modules"

# Push to the remote repository
git push origin HEAD
