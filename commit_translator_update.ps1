# commit_translator_update.ps1
# Stages, commits, and pushes the updated max_workers change in translator.py.
# Run this script from the repository root (d:\AUDIO SERIES AGENT).

git add translator.py

git commit -m "Update translate_text default max_workers to 40 for higher concurrency"

git push origin HEAD
