#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple demo runner - Execute all test cases via Flask API
Shows the frontend working with all tests passing
"""

import requests
import json
import time
import sys

API_BASE = "http://127.0.0.1:5001"

def run_demo():
    """Run the complete demo pipeline."""
    
    print("\n" + "="*80)
    print("  AI-Powered Agentic Test Automation System - DEMO EXECUTION")
    print("="*80)
    print(f"\nConnecting to API at: {API_BASE}")
    print("\n" + "-"*80)
    
    # Step 1: Fetch first test case
    print("\n[STEP 1] Fetching test case TC-001...")
    try:
        resp = requests.get(f"{API_BASE}/api/testcases/TC-001", timeout=5)
        if resp.status_code == 200:
            tc = resp.json()
            print(f"[OK] Test Case: {tc.get('name', 'TC-001')}")
            print(f"    Steps: {len(tc.get('steps', []))}")
            print(f"    Description: {tc.get('description', '')[:100]}...")
        else:
            print(f"[FAIL] Failed to fetch test case: {resp.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False
    
    # Step 2: Start pipeline execution
    print("\n[STEP 2] Starting pipeline execution with all 10 test cases...")
    
    test_case_ids = [f"TC-{i:03d}" for i in range(1, 11)]
    
    payload = {
        "test_case_ids": test_case_ids,
        "user_inputs": {},
        "max_retries": 3
    }
    
    try:
        resp = requests.post(f"{API_BASE}/api/pipeline/run", json=payload, timeout=5)
        if resp.status_code != 200:
            print(f"[FAIL] Failed to start pipeline: {resp.status_code}")
            print(f"    {resp.text}")
            return False
        
        run_data = resp.json()
        run_id = run_data.get('run_id')
        print(f"[OK] Pipeline started: {run_id}")
        print(f"    Test cases: {', '.join(test_case_ids)}")
        
    except Exception as e:
        print(f"[FAIL] Error starting pipeline: {e}")
        return False
    
    # Step 3: Stream execution events
    print("\n[STEP 3] Streaming execution events...")
    print("-"*80)
    
    try:
        resp = requests.get(f"{API_BASE}/api/pipeline/status/{run_id}", 
                           stream=True, timeout=180)
        
        events_received = 0
        passed_count = 0
        failed_count = 0
        final_summary = {}
        
        for line in resp.iter_lines(decode_unicode=True):
            if not line or not line.startswith('data: '):
                continue
            
            try:
                event_str = line[6:].strip()
                if not event_str:
                    continue
                    
                event = json.loads(event_str)
                event_type = event.get('type', '')
                
                # Format output based on event type
                if event_type == 'started':
                    print(f"[RUN] Pipeline started")
                
                elif event_type == 'phase':
                    phase = event.get('phase') or list(event.values())[0]
                    print(f"[*] {phase}")
                
                elif event_type == 'generate_ok':
                    msg = event.get('0') or event.get('message') or 'Test generation successful'
                    print(f"[OK] Generated: {msg}")
                
                elif event_type == 'completed':
                    summary = event.get('summary', {})
                    passed_count = summary.get('passed', 0)
                    failed_count = summary.get('failed', 0)
                    final_summary = summary
                    print(f"\n[OK] TESTS COMPLETED:")
                    print(f"    Total:  {summary.get('total', '?')}")
                    print(f"    Passed: {passed_count}")
                    print(f"    Failed: {failed_count}")
                
                elif event_type == 'error':
                    msg = event.get('message', 'Unknown error')
                    print(f"[ERROR] {msg}")
                
                elif event_type == 'done':
                    print(f"[OK] Pipeline completed")
                    break
                
                elif event_type != 'heartbeat':
                    # Log other events
                    print(f"[*] {event_type}: {str(event)[:100]}")
                
                events_received += 1
                
            except json.JSONDecodeError as e:
                continue
        
        print("-"*80)
        print(f"\nEvents received: {events_received}")
        
        # Final result
        success = failed_count == 0 and passed_count > 0
        
        if success:
            print("\n" + "="*80)
            print(f"  SUCCESS - ALL {passed_count} TESTS PASSED")
            print("="*80)
        else:
            print("\n" + "="*80)
            print(f"  Some tests failed - Passed: {passed_count}, Failed: {failed_count}")
            print("="*80)
        
        return success
        
    except requests.exceptions.Timeout:
        print("[FAIL] Pipeline execution timed out (>180s)")
        return False
    except Exception as e:
        print(f"[FAIL] Error during execution: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = run_demo()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n[FAIL] Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[FAIL] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
