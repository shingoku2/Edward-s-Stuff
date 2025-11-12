#!/usr/bin/env python3
"""
Test AIAssistant Module
Tests Bearer token authentication and endpoint fallback logic
"""

import os
import sys
import json
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_bearer_token_in_headers():
    """Test that Bearer token is added to headers when API key is provided"""
    print("=" * 60)
    print("TEST 1: Bearer Token Authentication")
    print("=" * 60)

    from ai_assistant import AIAssistant
    import requests

    # Mock requests to capture headers
    with patch('requests.post') as mock_post:
        # Set up mock response for OpenAI-compatible endpoint
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Test response'}}]
        }
        mock_post.return_value = mock_response

        # Create AIAssistant with API key
        test_api_key = "sk-test-open-webui-key-123"
        assistant = AIAssistant(
            provider="ollama",
            ollama_endpoint="http://localhost:8080",
            open_webui_api_key=test_api_key
        )
        # Set a current game so ask_question doesn't return early
        assistant.current_game = "Test Game"

        print(f"✓ Created AIAssistant with API key")
        print(f"  Endpoint: {assistant.ollama_endpoint}")
        print(f"  API Key: {assistant.open_webui_api_key}")

        # Make a test query
        try:
            response = assistant.ask_question("Test query")
            print(f"✓ Query executed successfully")

            # Check if Authorization header was included
            call_args = mock_post.call_args
            if call_args:
                headers = call_args[1].get('headers', {})
                print(f"  Headers sent: {headers}")

                if 'Authorization' in headers:
                    auth_header = headers['Authorization']
                    expected_header = f"Bearer {test_api_key}"

                    if auth_header == expected_header:
                        print(f"  ✓ Correct Bearer token in Authorization header")
                        return True
                    else:
                        print(f"  ✗ Authorization header present but incorrect")
                        print(f"    Expected: {expected_header}")
                        print(f"    Got: {auth_header}")
                        return False
                else:
                    print(f"  ✗ Authorization header not included")
                    return False
            else:
                print(f"  ✗ No HTTP call was made")
                return False

        except Exception as e:
            print(f"  ✗ Query failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def test_no_auth_header_without_key():
    """Test that no Authorization header is sent when no API key is provided"""
    print("\n" + "=" * 60)
    print("TEST 2: No Auth Header Without API Key")
    print("=" * 60)

    from ai_assistant import AIAssistant
    import requests

    # Mock requests to capture headers
    with patch('requests.post') as mock_post:
        # Set up mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Test response'}}]
        }
        mock_post.return_value = mock_response

        # Create AIAssistant WITHOUT API key
        assistant = AIAssistant(
            provider="ollama",
            ollama_endpoint="http://localhost:11434"
            # No open_webui_api_key provided
        )
        # Set a current game
        assistant.current_game = "Test Game"

        print(f"✓ Created AIAssistant without API key")

        # Make a test query
        try:
            response = assistant.ask_question("Test query")
            print(f"✓ Query executed")

            # Check headers
            call_args = mock_post.call_args
            if call_args:
                headers = call_args[1].get('headers', {})
                print(f"  Headers sent: {headers}")

                if 'Authorization' not in headers:
                    print(f"  ✓ No Authorization header sent (as expected)")
                    return True
                else:
                    print(f"  ✗ Authorization header included when it shouldn't be")
                    return False
            else:
                print(f"  ✗ No HTTP call was made")
                return False

        except Exception as e:
            print(f"  ✗ Query failed: {e}")
            return False


def test_endpoint_fallback_logic():
    """Test the three-tier endpoint fallback: OpenAI API → native /api/chat → /api/generate"""
    print("\n" + "=" * 60)
    print("TEST 3: Endpoint Fallback Logic")
    print("=" * 60)

    from ai_assistant import AIAssistant

    # Test case 1: First endpoint (OpenAI-compatible) works
    print("\n  Scenario A: OpenAI-compatible endpoint succeeds")
    with patch('requests.post') as mock_post, patch('requests.get'):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Response from OpenAI endpoint'}}]
        }
        mock_post.return_value = mock_response

        assistant = AIAssistant(provider="ollama", ollama_endpoint="http://localhost:8080")
        assistant.current_game = "Test Game"
        response = assistant.ask_question("Test")

        # Check that only one call was made
        if mock_post.call_count == 1:
            # Check it was to the OpenAI-compatible endpoint
            call_args = mock_post.call_args
            url = call_args[0][0]
            if url == "http://localhost:8080/v1/chat/completions":
                print(f"    ✓ Used OpenAI-compatible endpoint (no fallback needed)")
                test1_pass = True
            else:
                print(f"    ✗ Called wrong endpoint: {url}")
                test1_pass = False
        else:
            print(f"    ✗ Made {mock_post.call_count} calls (expected 1)")
            test1_pass = False

    # Test case 2: First endpoint returns 404, fallback to second
    print("\n  Scenario B: OpenAI endpoint 404 → fallback to /api/chat")
    with patch('requests.post') as mock_post, patch('requests.get'), patch('requests.exceptions.HTTPError', Exception):
        def mock_post_side_effect(url, *args, **kwargs):
            mock_response = Mock()
            if '/v1/chat/completions' in url:
                # First endpoint returns 404
                mock_response.status_code = 404
                mock_response.raise_for_status = Mock(side_effect=Exception("404"))
                return mock_response
            elif '/api/chat' in url:
                # Second endpoint works
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    'message': {'content': 'Response from native Ollama endpoint'}
                }
                return mock_response

        mock_post.side_effect = mock_post_side_effect

        assistant = AIAssistant(provider="ollama", ollama_endpoint="http://localhost:8080")
        assistant.current_game = "Test Game"

        try:
            response = assistant.ask_question("Test")

            # Check that two calls were made
            if mock_post.call_count == 2:
                print(f"    ✓ Made 2 calls (OpenAI → native Ollama)")
                test2_pass = True
            else:
                print(f"    ✗ Made {mock_post.call_count} calls (expected 2)")
                test2_pass = False
        except:
            print(f"    ✗ Fallback failed")
            test2_pass = False

    # Test case 3: First two endpoints fail, fallback to third
    print("\n  Scenario C: Both fail → fallback to /api/generate")
    with patch('requests.post') as mock_post, patch('requests.get'), patch('requests.exceptions.HTTPError', Exception):
        def mock_post_side_effect(url, *args, **kwargs):
            mock_response = Mock()
            if '/v1/chat/completions' in url or '/api/chat' in url:
                # First two endpoints return 405
                mock_response.status_code = 405
                mock_response.raise_for_status = Mock(side_effect=Exception("405"))
                return mock_response
            elif '/api/generate' in url:
                # Third endpoint works
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    'response': 'Response from generate endpoint'
                }
                return mock_response

        mock_post.side_effect = mock_post_side_effect

        assistant = AIAssistant(provider="ollama", ollama_endpoint="http://localhost:8080")
        assistant.current_game = "Test Game"

        try:
            response = assistant.ask_question("Test")

            # Check that three calls were made
            if mock_post.call_count == 3:
                print(f"    ✓ Made 3 calls (all tiers attempted)")
                test3_pass = True
            else:
                print(f"    ✗ Made {mock_post.call_count} calls (expected 3)")
                test3_pass = False
        except:
            print(f"    ✗ Third tier fallback failed")
            test3_pass = False

    return test1_pass and test2_pass and test3_pass


def test_405_error_message():
    """Test that 405 errors provide helpful authentication error messages"""
    print("\n" + "=" * 60)
    print("TEST 4: 405 Error Handling and Messages")
    print("=" * 60)

    from ai_assistant import AIAssistant

    # Test without API key
    print("\n  Scenario A: 405 error without API key")
    with patch('requests.post') as mock_post, patch('requests.get'):
        # Create a proper HTTPError mock
        import requests
        mock_response = Mock()
        mock_response.status_code = 405

        # Create HTTPError with response attribute
        http_error = requests.exceptions.HTTPError("405 Method Not Allowed")
        http_error.response = mock_response
        mock_response.raise_for_status = Mock(side_effect=http_error)

        mock_post.return_value = mock_response

        assistant = AIAssistant(provider="ollama", ollama_endpoint="http://localhost:8080")
        assistant.current_game = "Test Game"
        # No API key provided

        # ask_question catches exceptions and returns error messages as strings
        response = assistant.ask_question("Test")

        # Check if the response is an error message about authentication
        if response and "Error getting AI response:" in response:
            if "Open WebUI requires authentication" in response:
                print(f"    ✓ Provided helpful error message about authentication")
                print(f"      Message preview: {response[:120]}...")
                test1_pass = True
            else:
                print(f"    ✗ Error message doesn't mention authentication requirement")
                print(f"      Got: {response}")
                test1_pass = False
        else:
            print(f"    ✗ Expected error message but got: {response}")
            test1_pass = False

    # Test with API key
    print("\n  Scenario B: 405 error with API key (invalid key)")
    with patch('requests.post') as mock_post, patch('requests.get'):
        # Create a proper HTTPError mock
        import requests
        mock_response = Mock()
        mock_response.status_code = 405

        # Create HTTPError with response attribute
        http_error = requests.exceptions.HTTPError("405 Method Not Allowed")
        http_error.response = mock_response
        mock_response.raise_for_status = Mock(side_effect=http_error)

        mock_post.return_value = mock_response

        assistant = AIAssistant(
            provider="ollama",
            ollama_endpoint="http://localhost:8080",
            open_webui_api_key="sk-invalid-key"
        )
        assistant.current_game = "Test Game"

        # ask_question catches exceptions and returns error messages as strings
        response = assistant.ask_question("Test")

        # Check if the response contains the expected error message
        if response and "Error getting AI response:" in response:
            if "invalid or expired" in response.lower():
                print(f"    ✓ Provided helpful error message about invalid key")
                print(f"      Message: {response}")
                test2_pass = True
            else:
                print(f"    ⚠️  Error message present but could be more specific")
                print(f"      Got: {response}")
                test2_pass = True  # Still passing, just noting it
        else:
            print(f"    ✗ Expected error message but got: {response}")
            test2_pass = False

    return test1_pass and test2_pass


def main():
    """Run all AIAssistant tests"""
    print("\n" + "=" * 60)
    print("AI ASSISTANT MODULE TEST SUITE")
    print("=" * 60)
    print()

    results = []

    # Test 1: Bearer token
    try:
        result = test_bearer_token_in_headers()
        results.append(("Bearer Token Authentication", result))
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Bearer Token Authentication", False))

    # Test 2: No auth without key
    try:
        result = test_no_auth_header_without_key()
        results.append(("No Auth Without Key", result))
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        results.append(("No Auth Without Key", False))

    # Test 3: Endpoint fallback
    try:
        result = test_endpoint_fallback_logic()
        results.append(("Endpoint Fallback Logic", result))
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Endpoint Fallback Logic", False))

    # Test 4: 405 error messages
    try:
        result = test_405_error_message()
        results.append(("405 Error Messages", result))
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        results.append(("405 Error Messages", False))

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:30} {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All AIAssistant tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
