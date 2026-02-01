#!/bin/bash

# Usage: ./release.sh x.x.x
VERSION=$1

if [ -z "$VERSION" ]; then
  echo "Error: No version number provided. Usage: ./release.sh x.x.x"
  exit 1
fi

# Find the manifest.json file automatically inside custom_components/
MANIFEST_FILE=$(find custom_components -name "manifest.json" | head -n 1)

if [ -z "$MANIFEST_FILE" ]; then
  echo "Error: manifest.json not found in custom_components/"
  exit 1
fi

echo "Found manifest at: $MANIFEST_FILE"
echo "Preparing version v$VERSION..."

# 1. Update manifest.json
sed -i "s/\"version\": \".*\"/\"version\": \"$VERSION\"/g" "$MANIFEST_FILE"

# 2. Update version in README.md badge
# This looks for the pattern 'version-vX.X.X-blue' or 'version-X.X.X-blue'
if [ -f "README.md" ]; then
  sed -i "s/version-v[0-9.]*-blue/version-v$VERSION-blue/g" README.md
  sed -i "s/version-[0-9.]*-blue/version-$VERSION-blue/g" README.md
fi

echo "Commit new version"

# 3. Commit the changes
git add "$MANIFEST_FILE" README.md
git commit -m "Bump version to $VERSION"

# 4. Create a new tag
echo "Creating tag v$VERSION..."
git tag "v$VERSION"

# 5. Push to GitHub
echo "Pushing to GitHub..."
git push origin master
git push origin "v$VERSION"

echo "Success! Version v$VERSION is live."