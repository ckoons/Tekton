#!/bin/bash
# Create documentation directory structure for aish help system

echo "Creating documentation directories..."

# Base directories
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides

# List of all components
components=(
    "aish"
    "numa"
    "tekton" 
    "prometheus"
    "telos"
    "metis"
    "harmonia"
    "synthesis"
    "athena"
    "sophia"
    "noesis"
    "engram"
    "apollo"
    "rhetor"
    "penia"
    "hermes"
    "ergon"
    "terma"
)

# Create directories for each component
for component in "${components[@]}"; do
    echo "Creating directories for $component..."
    mkdir -p "/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/$component"
    mkdir -p "/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides/$component"
    
    # Create placeholder README files
    echo "# $component CI Training" > "/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/$component/README.md"
    echo "" >> "/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/$component/README.md"
    echo "Training documentation for Companion Intelligences working with $component." >> "/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/$component/README.md"
    
    echo "# $component User Guide" > "/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides/$component/README.md"
    echo "" >> "/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides/$component/README.md"
    echo "User guide for humans working with $component." >> "/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides/$component/README.md"
done

# Create root README files
echo "# CI Training Documentation" > /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/README.md
echo "" >> /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/README.md
echo "This directory contains training materials for Companion Intelligences working with Tekton." >> /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/README.md

echo "# User Guide Documentation" > /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides/README.md
echo "" >> /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides/README.md
echo "This directory contains guides for human users working with Tekton." >> /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides/README.md

echo "Documentation directories created successfully!"