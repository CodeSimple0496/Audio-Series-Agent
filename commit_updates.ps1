# commit_updates.ps1
# This script stages, commits, and pushes the recent performance enhancements.
# Run it from the repository root (d:\AUDIO SERIES AGENT).

# Stage changed files and new files
git add .

# Commit with a descriptive message
git commit -m "Fix LRUCache API method in translator, resolve IndentationError in scraper, and finalize optimizations"

# Push to the remote repository
git push origin HEAD
