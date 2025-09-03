#!/bin/bash

# Release script for Baby Care Tracker Add-on
# This script creates a GitHub release and pushes version tags

set -e

VERSION=$1

if [ -z "$VERSION" ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 1.0.3"
    exit 1
fi

echo "Creating release for version $VERSION"

# Check if we're in the right directory
if [ ! -f "baby-care-tracker/config.yaml" ]; then
    echo "Error: Must be run from the add-on repository root"
    exit 1
fi

# Create and push git tag
echo "Creating git tag v$VERSION"
git tag -a "v$VERSION" -m "Release version $VERSION"
git push origin "v$VERSION"

echo "Tag v$VERSION created and pushed successfully"
echo ""
echo "Next steps:"
echo "1. Go to GitHub and create a release from the tag"
echo "2. Or use GitHub CLI: gh release create v$VERSION --title 'v$VERSION' --notes-from-tag"
echo "3. Refresh your Home Assistant add-on repository"
