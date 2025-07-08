#!/bin/bash
# Test script for aish purpose functionality - demonstrates all three operations

echo "=== Testing aish purpose command - THREE OPERATIONS ==="
echo

echo "==== OPERATION 1: Show current terminal's purpose with playbook ===="
echo "Command: aish purpose"
echo "Expected: Shows current terminal's purpose and relevant playbook content"
echo "Running..."
aish purpose
echo

echo "==== OPERATION 2: Query another terminal's purpose (simple) ===="
echo "Command: aish purpose amy"
echo "Expected: Simple output like 'Amy: Coding, Research'"
echo "Running..."
aish purpose amy
echo

echo "==== OPERATION 3: Update a terminal's purpose ===="
echo "Command: aish purpose amy \"Coding, Research\""
echo "Expected: Updates Amy's purpose and shows playbook content"
echo "Running..."
aish purpose amy "Coding, Research"
echo

echo "=== Additional Tests ==="
echo

echo "1. List all terminals to see purposes:"
aish terma list
echo

echo "2. Test purpose-based routing with @coding:"
echo "Running: aish terma @coding \"Test message to all coders\""
aish terma @coding "Test message to all coders"
echo

echo "3. Test prompt with purpose routing:"
echo "Running: aish prompt @research \"Important research update\""
aish prompt @research "Important research update"
echo

echo "=== Purpose System Features ==="
echo "✓ Word-based matching: @coding matches terminals with 'Coding' in purpose"
echo "✓ Case insensitive: 'coding', 'Coding', 'CODING' all work"
echo "✓ CSV support: 'Coding, Research' creates two separate purposes"
echo "✓ Playbook integration: Shows relevant documentation for each purpose"
echo "✓ Environment update: Sends heartbeat command to update TEKTON_TERMINAL_PURPOSE"
echo "✓ CI notification: Terminal receives message when purpose changes"
echo

echo "=== Manual Verification Steps ==="
echo "1. Launch a test terminal: tekton-launch -n TestCI"
echo "2. Set purpose: aish purpose TestCI \"Testing, Development\""
echo "3. Check TestCI received: 'Your purpose has been updated to: Testing, Development'"
echo "4. Query purpose: aish purpose TestCI (should show 'TestCI: Testing, Development')"
echo "5. Test routing: aish terma @testing \"Hello testers\""