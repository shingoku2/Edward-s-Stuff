#!/bin/bash
# Run all test suites

echo "======================================================================"
echo "COMPREHENSIVE TEST SUITE FOR OPEN WEBUI INTEGRATION"
echo "======================================================================"
echo ""

TESTS_PASSED=0
TESTS_FAILED=0

# Test 1: Syntax validation
echo "Running syntax validation tests..."
python test_config_module.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Configuration module tests: PASSED"
    ((TESTS_PASSED++))
else
    echo "❌ Configuration module tests: FAILED"
    ((TESTS_FAILED++))
fi

# Test 2: AI Assistant module
echo "Running AIAssistant module tests..."
python test_ai_assistant.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ AIAssistant module tests: PASSED"
    ((TESTS_PASSED++))
else
    echo "❌ AIAssistant module tests: FAILED"
    ((TESTS_FAILED++))
fi

# Test 3: GUI components
echo "Running GUI components tests..."
python test_gui_components.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ GUI components tests: PASSED"
    ((TESTS_PASSED++))
else
    echo "❌ GUI components tests: FAILED"
    ((TESTS_FAILED++))
fi

echo ""
echo "======================================================================"
echo "TEST SUMMARY"
echo "======================================================================"
echo "Passed: $TESTS_PASSED"
echo "Failed: $TESTS_FAILED"
echo "Total:  $((TESTS_PASSED + TESTS_FAILED))"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo "🎉 ALL TESTS PASSED!"
    exit 0
else
    echo "⚠️  SOME TESTS FAILED"
    exit 1
fi
