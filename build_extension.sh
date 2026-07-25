#!/bin/bash
# Builds the Browser Companion extension for distribution.

echo "Building Solomon Browser Companion..."
BUILD_DIR="build"
ZIP_NAME="solomon_browser_companion.zip"

# Create a clean build directory
rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR

# Copy extension files, omitting OS/dev artifacts
rsync -av --progress browser_extension/ $BUILD_DIR/ \
  --exclude ".DS_Store" \
  --exclude "__pycache__" \
  --exclude "*.py" \
  --exclude "*.md"

# Zip the contents of the build directory
cd $BUILD_DIR
zip -r ../$ZIP_NAME *
cd ..

# Cleanup build directory
rm -rf $BUILD_DIR

echo "Build complete: $ZIP_NAME"
