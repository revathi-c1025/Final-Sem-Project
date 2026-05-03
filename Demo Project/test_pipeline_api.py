#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script to run the demo via the Flask API
Shows how the frontend interacts with the backend
"""

import requests
import json
import time
import sys

API_URL = "http://127.0.0.1:5001"

def test_pipeline_execution():
    """Test the pipeline execution via API."""
    
    print("\n" + "="*70)
    print("AI Test Automation - Pipeline API Test")
    print("="*70)
    
    # Get test cases
    print("\n[1] Fetching available test cases...")
    response = requests.get(f"{API_URL}/api/testcases")
    if response.status_code != 200:
        print(f"[X] Failed to fetch test cases: {response.status_code}")
        return False
    
    test_cases = response.json()
    print(f"[OK] Found {len(test_cases)} test cases:")
    for tc in test_cases[:3]:
        print(f"     - {tc.get('id', 'N/A')}: {tc.get('name', 'N/A')}")
    
    # Select all test cases to run
    test_case_ids = [tc.get('id') for tc in test_cases]
    
    # Start pipeline
    print(f"\n[2] Starting pipeline with {len(test_case_ids)} test cases...")
    run_data = {
        "test_case_ids": test_case_ids,
        "user_inputs": {},
        "max_retries": 3
    }
    
    response = requests.post(f"{API_URL}/api/pipeline/run", json=run_data)
    if response.status_code != 200:
        print(f"[X] Failed to start pipeline: {response.status_code}")
        print(f"    Response: {response.text}")
        return False
    
    result = response.json()
    run_id = result.get('run_id')
    print(f"[OK] Pipeline started with run_id: {run_id}")
    
    # Stream events
    print(f"\n[3] Streaming pipeline events...")
    print("-"*70)
    
    event_stream_url = f"{API_URL}/api/pipeline/status/{run_id}"
    try:
        response = requests.get(event_stream_url, stream=True, timeout=120)
        
        event_count = 0
        passed_count = 0
        failed_count = 0
        
        for line in response.iter_lines():
            if line:
                try:
                    line = line.decode('utf-8') if isinstance(line, bytes) else line
                    if line.startswith('data: '):
                        event_json = line[6:]
                        event = json.loads(event_json)
                        
                        event_type = event.get('type')
                        
                        if event_type == 'started':
                            print(f"[START] Pipeline started")
                        elif event_type == 'phase':
                            print(f"[PHASE] {event.get('phase', 'Unknown')}")
                        elif event_type == 'generate_ok':
                            print(f"[GEN OK] {event.get('0', event.get('message', 'Generated'))}")
                        elif event_type == 'generate_fail':
                            print(f"[GEN FAIL] {event.get('0', event.get('message', 'Generation failed'))}")
                        elif event_type == 'completed':
                            summary = event.get('summary', {})
                            passed = summary.get('passed', 0)
                            failed = summary.get('failed', 0)
                            print(f"[COMPLETED] Tests Passed: {passed}, Failed: {failed}")
                            passed_count = passed
                            failed_count = failed
                        elif event_type == 'error':
                            print(f"[ERROR] {event.get('message', 'Unknown error')}")
                        elif event_type == 'done':
                            print(f"[DONE] Pipeline execution completed")
                            break
                        elif event_type != 'heartbeat':
                            print(f"[{event_type.upper()}] {json.dumps(event)}")
                        
                        event_count += 1
                except json.JSONDecodeError:
                    pass
                except Exception as e:
                    print(f"[ERROR] Processing event: {e}")
                    continue
        
        print("-"*70)
        print(f"\n[OK] Pipeline completed with {event_count} events")
        print(f"     Passed: {passed_count}")
        print(f"     Failed: {failed_count}")
        
        return failed_count == 0
        
    except requests.exceptions.Timeout:
        print("[X] Pipeline execution timed out")
        return False
    except Exception as e:
        print(f"[X] Error streaming events: {e}")
        return False

if __name__ == "__main__":
    success = test_pipeline_execution()
    sys.exit(0 if success else 1)
