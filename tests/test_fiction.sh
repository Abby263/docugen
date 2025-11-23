#!/bin/bash

# Script to test fiction generation functionality

echo "Testing fiction generation functionality..."

# Use single quotes to wrap the entire query to avoid shell parsing issues
python main_agent.py search 'Write a locked room mystery short story; the story should be told from the murderer'\''s perspective, but only reveal "I am the murderer" at the end'
