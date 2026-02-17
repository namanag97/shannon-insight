#!/bin/bash

#################################################################################
# init_git_history.sh
#
# Initializes realistic git history for the polyglot_baseline test fixture.
# Creates multiple authors, timestamps, and commit patterns for testing:
#   - Author patterns (Alice, Bob, Charlie)
#   - Co-change patterns (Python service routes + handlers always together)
#   - Churn patterns (10 commits in 1 week on Python API routes)
#   - Single-author files (TypeScript storage utilities by Charlie only)
#   - Bug fix patterns ("fix:" prefix for fix_ratio testing)
#
# Usage: ./init_git_history.sh
#
#################################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}Initializing git history for polyglot_baseline fixture...${NC}"

# Verify we're in the right directory
if [[ ! -d "$SCRIPT_DIR/python_service" ]] || [[ ! -d "$SCRIPT_DIR/go_backend" ]] || [[ ! -d "$SCRIPT_DIR/ts_frontend" ]]; then
    echo -e "${RED}Error: Expected directories (python_service, go_backend, ts_frontend) not found${NC}"
    exit 1
fi

cd "$SCRIPT_DIR"

# Initialize git repo if not already initialized
if [[ ! -d .git ]]; then
    git init
    git config user.name "Alice Developer"
    git config user.email "alice@company.com"
    echo "Initialized git repository"
else
    echo "Git repository already initialized"
fi

#################################################################################
# Helper functions for creating commits with specific authors and dates
#################################################################################

# Create a commit with specific author and date
# Usage: commit_as "Author Name" "email@example.com" "YYYY-MM-DD HH:MM:SS" "commit message" [files...]
commit_as() {
    local author_name="$1"
    local author_email="$2"
    local commit_date="$3"
    local commit_msg="$4"
    shift 4
    local files=("$@")

    # Convert date to Unix timestamp for use with GIT_AUTHOR_DATE
    # Use gdate if available (GNU coreutils), fall back to date command
    local timestamp
    if command -v gdate &> /dev/null; then
        timestamp=$(gdate -d "$commit_date" "+%s" 2>/dev/null || date -j -f "%Y-%m-%d %H:%M:%S" "$commit_date" "+%s")
    else
        timestamp=$(date -j -f "%Y-%m-%d %H:%M:%S" "$commit_date" "+%s")
    fi

    local tz_offset="+0000"
    local date_str="$timestamp $tz_offset"

    # Stage the specified files
    for file in "${files[@]}"; do
        git add "$file" 2>/dev/null || true
    done

    # Create commit with specific author and timestamp
    GIT_AUTHOR_NAME="$author_name" \
    GIT_AUTHOR_EMAIL="$author_email" \
    GIT_AUTHOR_DATE="$date_str" \
    GIT_COMMITTER_NAME="$author_name" \
    GIT_COMMITTER_EMAIL="$author_email" \
    GIT_COMMITTER_DATE="$date_str" \
    git commit -m "$commit_msg" 2>/dev/null || true

    echo "  ✓ $commit_msg"
}

#################################################################################
# Helper for date calculation (handles both macOS and GNU date)
#################################################################################

calc_date() {
    local offset="$1"  # e.g., "-6m", "-5m", "+2d", etc.
    local format="${2:-%Y-%m-%d %H:%M:%S}"

    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        date -v"$offset" "+$format"
    else
        # GNU date (Linux)
        date -d "$offset" "+$format"
    fi
}

#################################################################################
# Phase 1: Initial commit (6 months ago)
# Alice creates baseline code for all three services
#################################################################################

echo -e "\n${BLUE}Phase 1: Initial commit (6 months ago)${NC}"

# Calculate date 6 months ago
INITIAL_DATE=$(calc_date "-6m")

git add -A
commit_as "Alice Developer" "alice@company.com" "$INITIAL_DATE" \
    "Initial: Add python_service, go_backend, ts_frontend base code" \
    python_service/__init__.py python_service/config.py python_service/exceptions.py \
    python_service/models python_service/api python_service/utils \
    go_backend/main.go go_backend/handlers go_backend/services go_backend/models \
    ts_frontend/components ts_frontend/hooks ts_frontend/types ts_frontend/utils

#################################################################################
# Phase 2: Regular feature development (5-4 months ago)
# Mix of Alice and Bob commits on different services
#################################################################################

echo -e "\n${BLUE}Phase 2: Regular feature development (5-4 months ago)${NC}"

# Feature 1: Python service authentication (Alice)
DATE_5M=$(calc_date "-5m" "%Y-%m-%d")
echo "# Authentication module" >> python_service/api/__init__.py
commit_as "Alice Developer" "alice@company.com" "$DATE_5M 10:30:00" \
    "feat: Add authentication middleware to Python service" \
    python_service/api/__init__.py

# Feature 2: Go backend user handlers (Bob)
DATE_5M_1=$(calc_date "-5m+2d" "%Y-%m-%d")
echo "// User authorization middleware" >> go_backend/handlers/user_handler.go
commit_as "Bob Engineer" "bob@company.com" "$DATE_5M_1 11:00:00" \
    "feat: Add user authorization in Go handlers" \
    go_backend/handlers/user_handler.go

# Feature 3: TypeScript frontend hooks (Charlie)
DATE_5M_2=$(calc_date "-5m+4d" "%Y-%m-%d")
echo "// Custom hooks for state management" >> ts_frontend/hooks/index.ts
commit_as "Charlie Intern" "charlie@company.com" "$DATE_5M_2 14:15:00" \
    "feat: Add custom React hooks for state management" \
    ts_frontend/hooks/index.ts

# Feature 4: Python service database models (Alice)
DATE_5M_3=$(calc_date "-5m+6d" "%Y-%m-%d")
echo "# Database connection pool" >> python_service/models/__init__.py
commit_as "Alice Developer" "alice@company.com" "$DATE_5M_3 09:45:00" \
    "feat: Add database connection pooling" \
    python_service/models/__init__.py

#################################################################################
# Phase 3: Co-change pattern setup (4 months ago)
# Start establishing co-change between go_backend handlers and services
#################################################################################

echo -e "\n${BLUE}Phase 3: Co-change pattern commits (4 months ago)${NC}"

DATE_4M=$(calc_date "-4m" "%Y-%m-%d")

# Co-change commit 1: User service refactor (both files together)
echo "// Updated user service methods" >> go_backend/services/user_service.go
echo "// Updated user handlers with new methods" >> go_backend/handlers/user_handler.go
commit_as "Alice Developer" "alice@company.com" "$DATE_4M 10:00:00" \
    "refactor: Refactor user service and handlers (co-change pattern)" \
    go_backend/services/user_service.go go_backend/handlers/user_handler.go

# Co-change commit 2: More user service work
DATE_4M_1=$(calc_date "-4m+3d" "%Y-%m-%d")
echo "// Add caching to user service" >> go_backend/services/user_service.go
echo "// Add cache invalidation to handlers" >> go_backend/handlers/user_handler.go
commit_as "Bob Engineer" "bob@company.com" "$DATE_4M_1 15:30:00" \
    "feat: Add user service caching" \
    go_backend/services/user_service.go go_backend/handlers/user_handler.go

#################################################################################
# Phase 4: Charlie's isolated work on TypeScript storage (3.5 months ago)
# Only Charlie touches storage.ts - creates single-author (truck factor) risk
#################################################################################

echo -e "\n${BLUE}Phase 4: Charlie's isolated TypeScript storage work (3.5 months ago)${NC}"

DATE_3_5M=$(calc_date "-3m-15d" "%Y-%m-%d")
echo "// Storage initialization" >> ts_frontend/utils/storage.ts
commit_as "Charlie Intern" "charlie@company.com" "$DATE_3_5M 08:00:00" \
    "feat: Initialize storage utility module" \
    ts_frontend/utils/storage.ts

DATE_3_5M_1=$(calc_date "-3m-12d" "%Y-%m-%d")
echo "// Add localStorage wrapper" >> ts_frontend/utils/storage.ts
commit_as "Charlie Intern" "charlie@company.com" "$DATE_3_5M_1 10:20:00" \
    "feat: Add localStorage wrapper functions" \
    ts_frontend/utils/storage.ts

DATE_3_5M_2=$(calc_date "-3m-10d" "%Y-%m-%d")
echo "// Add session storage utilities" >> ts_frontend/utils/storage.ts
commit_as "Charlie Intern" "charlie@company.com" "$DATE_3_5M_2 13:45:00" \
    "feat: Add sessionStorage utilities" \
    ts_frontend/utils/storage.ts

DATE_3_5M_3=$(calc_date "-3m-8d" "%Y-%m-%d")
echo "// Add encryption for sensitive data" >> ts_frontend/utils/storage.ts
commit_as "Charlie Intern" "charlie@company.com" "$DATE_3_5M_3 11:00:00" \
    "feat: Add encryption for sensitive storage" \
    ts_frontend/utils/storage.ts

#################################################################################
# Phase 5: Python service API churn (3 months ago)
# 10 commits in 1 week simulating iterative development/debugging
#################################################################################

echo -e "\n${BLUE}Phase 5: Python API route churn - 10 commits in 1 week (3 months ago)${NC}"

for i in {1..10}; do
    # Calculate date: spread across 7 days
    day_offset=$((i - 1))
    commit_date=$(calc_date "-3m+${day_offset}d" "%Y-%m-%d")
    hour=$((9 + i % 8))
    commit_time="${commit_date} ${hour}:30:00"

    # Alternate between small features and bug fixes
    if [ $((i % 3)) -eq 0 ]; then
        echo "# Fix in route $i" >> python_service/api/routes.py
        commit_as "Alice Developer" "alice@company.com" "$commit_time" \
            "fix: Fix routing issue #$i in API endpoints" \
            python_service/api/routes.py
    else
        echo "# Enhancement $i to routes" >> python_service/api/routes.py
        commit_as "Alice Developer" "alice@company.com" "$commit_time" \
            "refactor: Optimize API route handling (iteration $i)" \
            python_service/api/routes.py
    fi
done

#################################################################################
# Phase 6: Bug fixes with "fix:" prefix (2 months ago)
# Multiple bug fix commits for fix_ratio calculation
#################################################################################

echo -e "\n${BLUE}Phase 6: Bug fix commits for fix_ratio testing (2 months ago)${NC}"

DATE_2M=$(calc_date "-2m" "%Y-%m-%d")
echo "# Fix for edge case in error handling" >> python_service/exceptions.py
commit_as "Alice Developer" "alice@company.com" "$DATE_2M 10:00:00" \
    "fix: Handle edge case in exception middleware" \
    python_service/exceptions.py

DATE_2M_1=$(calc_date "-2m+3d" "%Y-%m-%d")
echo "// Fix goroutine leak in handlers" >> go_backend/handlers/user_handler.go
commit_as "Bob Engineer" "bob@company.com" "$DATE_2M_1 14:20:00" \
    "fix: Prevent goroutine leak in request handlers" \
    go_backend/handlers/user_handler.go

DATE_2M_2=$(calc_date "-2m+5d" "%Y-%m-%d")
echo "// Fix memory leak in event listeners" >> ts_frontend/hooks/index.ts
commit_as "Charlie Intern" "charlie@company.com" "$DATE_2M_2 11:45:00" \
    "fix: Clean up event listeners to prevent memory leaks" \
    ts_frontend/hooks/index.ts

DATE_2M_3=$(calc_date "-2m+7d" "%Y-%m-%d")
echo "# Fix: Handle concurrent requests properly" >> python_service/utils/__init__.py
commit_as "Alice Developer" "alice@company.com" "$DATE_2M_3 09:15:00" \
    "fix: Handle concurrent request race condition" \
    python_service/utils/__init__.py

#################################################################################
# Phase 7: More recent work (1 month ago to present)
# Mix of all authors with varied commit patterns
#################################################################################

echo -e "\n${BLUE}Phase 7: Recent development (1 month ago to present)${NC}"

DATE_1M=$(calc_date "-1m" "%Y-%m-%d")
echo "# Performance optimization" >> python_service/config.py
commit_as "Alice Developer" "alice@company.com" "$DATE_1M 10:00:00" \
    "perf: Add caching layer to configuration loading" \
    python_service/config.py

DATE_1M_1=$(calc_date "-1m+5d" "%Y-%m-%d")
echo "// Add metrics collection" >> go_backend/services/user_service.go
commit_as "Bob Engineer" "bob@company.com" "$DATE_1M_1 13:30:00" \
    "feat: Add Prometheus metrics to user service" \
    go_backend/services/user_service.go

DATE_1M_2=$(calc_date "-1m+10d" "%Y-%m-%d")
echo "// Fix TypeScript types" >> ts_frontend/types/index.ts
commit_as "Charlie Intern" "charlie@company.com" "$DATE_1M_2 15:00:00" \
    "fix: Correct TypeScript type definitions" \
    ts_frontend/types/index.ts

# One more co-change commit to reinforce the pattern
DATE_1M_3=$(calc_date "-1m+15d" "%Y-%m-%d")
echo "// Update user service with new fields" >> go_backend/services/user_service.go
echo "// Handle new fields in user handler" >> go_backend/handlers/user_handler.go
commit_as "Alice Developer" "alice@company.com" "$DATE_1M_3 11:20:00" \
    "feat: Add profile fields to user service and handlers" \
    go_backend/services/user_service.go go_backend/handlers/user_handler.go

#################################################################################
# Verification and Summary
#################################################################################

echo -e "\n${GREEN}✓ Git history initialization complete!${NC}"

# Display summary statistics
echo -e "\n${BLUE}Summary Statistics:${NC}"
echo "Total commits: $(git rev-list --count HEAD)"
echo "Authors:"
git shortlog -sn --summary
echo ""
echo "Most-changed files:"
git log --oneline --name-only | grep -v '^$' | sort | uniq -c | sort -rn | head -10
echo ""

# Show commits for key files
echo -e "${BLUE}Key file commit history:${NC}"
echo "python_service/api/routes.py:"
git log --oneline -- python_service/api/routes.py | wc -l | xargs echo "  Commits:"

echo "go_backend/services/user_service.go + go_backend/handlers/user_handler.go (co-change):"
git log --oneline -- go_backend/services/user_service.go | wc -l | xargs echo "  Co-changes:"

echo "ts_frontend/utils/storage.ts (single author):"
git log --oneline --format="%an" -- ts_frontend/utils/storage.ts | sort | uniq -c

echo -e "\n${GREEN}Ready for testing!${NC}"
