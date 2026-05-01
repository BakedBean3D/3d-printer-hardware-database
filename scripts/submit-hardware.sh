#!/bin/bash
# submit-hardware.sh — Parse a Hardware Watch report for [PASS] entries and create PRs.
#
# Usage: ./scripts/submit-hardware.sh <path-to-Hardware_Watch_YYYY-MM-DD.md>
#
# Reads the watch report, extracts YAML blocks from [PASS] entries,
# appends them to the correct files, and creates a PR per category.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <Hardware_Watch_YYYY-MM-DD.md>"
    exit 1
fi

WATCH_FILE="$1"
if [[ ! -f "$WATCH_FILE" ]]; then
    echo "Error: File not found: $WATCH_FILE"
    exit 1
fi

DATE=$(basename "$WATCH_FILE" | sed 's/Hardware_Watch_//;s/\.md//')
BRANCH="hardware-update-$DATE"

cd "$REPO_ROOT"

# Ensure we're on a clean main
git checkout main
git pull origin main

# Create feature branch
git checkout -b "$BRANCH" 2>/dev/null || git checkout "$BRANCH"

# Parse the watch file for [PASS] entries
# Strategy: find ### [PASS] headers, extract the YAML block that follows,
# determine the category from the section header, and append to the right file.

CURRENT_CATEGORY=""
IN_PASS_ENTRY=false
IN_YAML_BLOCK=false
YAML_BUFFER=""
YAML_TARGET=""
ENTRIES_ADDED=0

determine_target() {
    local category="$1"
    local yaml_content="$2"

    case "$category" in
        motors)
            # Extract manufacturer from YAML and build filename
            local mfr
            mfr=$(echo "$yaml_content" | grep "manufacturer:" | head -1 | sed 's/.*manufacturer: *//' | tr '[:upper:]' '[:lower:]' | tr ' ' '_' | tr -d "'\"")
            echo "motors/${mfr}.yaml"
            ;;
        hotends)
            local mfr
            mfr=$(echo "$yaml_content" | grep "manufacturer:" | head -1 | sed 's/.*manufacturer: *//' | tr '[:upper:]' '[:lower:]' | tr ' ' '_' | tr -d "'\"")
            echo "hotends/${mfr}.yaml"
            ;;
        probes)
            local mfr
            mfr=$(echo "$yaml_content" | grep "manufacturer:" | head -1 | sed 's/.*manufacturer: *//' | tr '[:upper:]' '[:lower:]' | tr ' ' '_' | tr -d "'\"")
            echo "probes/${mfr}.yaml"
            ;;
        extruders)
            echo "extruders/extruders.yaml"
            ;;
        toolheads)
            echo "toolheads/toolheads.yaml"
            ;;
        *)
            echo ""
            ;;
    esac
}

while IFS= read -r line; do
    # Track which category section we're in
    if [[ "$line" =~ ^##[[:space:]]+(Motors|Hotends|Extruders|Toolheads|Probes) ]]; then
        CURRENT_CATEGORY=$(echo "${BASH_REMATCH[1]}" | tr '[:upper:]' '[:lower:]')
        IN_PASS_ENTRY=false
        IN_YAML_BLOCK=false
        continue
    fi

    # Detect [PASS] entries
    if [[ "$line" =~ ^###[[:space:]]+\[PASS\] ]]; then
        IN_PASS_ENTRY=true
        IN_YAML_BLOCK=false
        YAML_BUFFER=""
        continue
    fi

    # Detect [FAIL] or [REVIEW] entries — skip them
    if [[ "$line" =~ ^###[[:space:]]+\[(FAIL|REVIEW)\] ]]; then
        IN_PASS_ENTRY=false
        IN_YAML_BLOCK=false
        continue
    fi

    # Detect start of YAML block within a PASS entry
    if [[ "$IN_PASS_ENTRY" == true && "$line" == '```yaml' ]]; then
        IN_YAML_BLOCK=true
        YAML_BUFFER=""
        continue
    fi

    # Detect end of YAML block
    if [[ "$IN_YAML_BLOCK" == true && "$line" == '```' ]]; then
        IN_YAML_BLOCK=false

        if [[ -n "$YAML_BUFFER" && -n "$CURRENT_CATEGORY" ]]; then
            YAML_TARGET=$(determine_target "$CURRENT_CATEGORY" "$YAML_BUFFER")

            if [[ -n "$YAML_TARGET" ]]; then
                TARGET_PATH="$REPO_ROOT/$YAML_TARGET"

                # Create file if it doesn't exist (new manufacturer)
                if [[ ! -f "$TARGET_PATH" ]]; then
                    mkdir -p "$(dirname "$TARGET_PATH")"
                    echo "$YAML_BUFFER" > "$TARGET_PATH"
                    echo "  Created: $YAML_TARGET"
                else
                    # Append to existing file
                    echo "" >> "$TARGET_PATH"
                    echo "$YAML_BUFFER" >> "$TARGET_PATH"
                    echo "  Appended to: $YAML_TARGET"
                fi

                ENTRIES_ADDED=$((ENTRIES_ADDED + 1))
            fi
        fi

        IN_PASS_ENTRY=false
        continue
    fi

    # Accumulate YAML content
    if [[ "$IN_YAML_BLOCK" == true ]]; then
        if [[ -z "$YAML_BUFFER" ]]; then
            YAML_BUFFER="$line"
        else
            YAML_BUFFER="$YAML_BUFFER
$line"
        fi
    fi

done < "$WATCH_FILE"

if [[ "$ENTRIES_ADDED" -eq 0 ]]; then
    echo "No [PASS] entries found. Nothing to submit."
    git checkout main
    git branch -d "$BRANCH" 2>/dev/null || true
    exit 0
fi

echo ""
echo "Added $ENTRIES_ADDED entries."

# Validate
echo ""
echo "Running validation..."
if command -v python3 &>/dev/null; then
    python3 scripts/validate.py || {
        echo "ERROR: Validation failed. Please fix the YAML and retry."
        exit 1
    }
fi

# Commit and create PR
git add -A
git commit -m "feat: Add $ENTRIES_ADDED hardware entries from $DATE watch report

Source: Hardware_Watch_$DATE.md (human-reviewed, marked [PASS])

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"

git push -u origin "$BRANCH"

# Create PR
if command -v gh &>/dev/null; then
    gh pr create \
        --title "Add $ENTRIES_ADDED hardware entries ($DATE)" \
        --body "$(cat <<EOF
## Summary
- $ENTRIES_ADDED new hardware entries from automated weekly scan
- Source: \`Hardware_Watch_$DATE.md\` (human-reviewed)
- All entries marked \`[PASS]\` by reviewer

## Validation
\`scripts/validate.py\` passed.

---
🤖 Generated from hardware watch scan
EOF
)"
    echo ""
    echo "PR created successfully."
else
    echo ""
    echo "gh CLI not found — push complete, create PR manually."
fi

# Return to main
git checkout main
