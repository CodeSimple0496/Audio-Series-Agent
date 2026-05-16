# commit_updates.ps1
# This script stages, commits, and pushes the recent performance enhancements.
# Run it from the repository root (d:\AUDIO SERIES AGENT).

# Stage changed files and new files
git add .

# Commit with a descriptive message
git commit -m "Optimize audio merging to O(N log N) tree merge, limit audio workers for stability, fix translation cache, fix UI progress bar, and set optimal worker count to 20"

# Push to the remote repository
git push origin HEAD
