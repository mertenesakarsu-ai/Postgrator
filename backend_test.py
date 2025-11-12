#!/usr/bin/env python3
"""
Backend Test Suite for MSSQL BAK to PostgreSQL Migration Tool
Tests the demo migration functionality
"""

import requests
import time
import json
import sys
from typing import Dict, Any

# Backend URL from frontend/.env
BACKEND_URL = "https://local-dev-env.preview.emergentagent.com/api"

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_pass(self, test_name: str):
        self.passed += 1
        print(f"✅ PASS: {test_name}")
    
    def add_fail(self, test_name: str, error: str):
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        print(f"❌ FAIL: {test_name} - {error}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY: {self.passed}/{total} tests passed")
        if self.errors:
            print(f"\nFAILED TESTS:")
            for error in self.errors:
                print(f"  - {error}")
        print(f"{'='*60}")
        return self.failed == 0

def test_api_health():
    """Test if the API is accessible"""
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "message" in data:
                return True, "API is accessible"
        return False, f"Unexpected response: {response.status_code}"
    except Exception as e:
        return False, f"API not accessible: {str(e)}"

def test_demo_migration_start():
    """Test POST /api/import/demo endpoint"""
    try:
        response = requests.post(f"{BACKEND_URL}/import/demo", timeout=30)
        
        if response.status_code != 200:
            return False, f"HTTP {response.status_code}: {response.text}", None
        
        data = response.json()
        
        # Check required fields
        required_fields = ["jobId", "status", "demo"]
        for field in required_fields:
            if field not in data:
                return False, f"Missing field: {field}", None
        
        # Check values
        if data["status"] != "queued":
            return False, f"Expected status 'queued', got '{data['status']}'", None
        
        if data["demo"] != True:
            return False, f"Expected demo=true, got demo={data['demo']}", None
        
        job_id = data["jobId"]
        if not job_id or len(job_id) < 10:
            return False, f"Invalid job ID: {job_id}", None
        
        return True, "Demo migration started successfully", job_id
        
    except Exception as e:
        return False, f"Request failed: {str(e)}", None

def test_job_status(job_id: str):
    """Test GET /api/jobs/{job_id} endpoint"""
    try:
        # Wait a bit for job to start
        time.sleep(2)
        
        response = requests.get(f"{BACKEND_URL}/jobs/{job_id}", timeout=10)
        
        if response.status_code != 200:
            return False, f"HTTP {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Check required fields
        required_fields = ["jobId", "status", "stage", "percent", "stats"]
        for field in required_fields:
            if field not in data:
                return False, f"Missing field: {field}"
        
        # Check job ID matches
        if data["jobId"] != job_id:
            return False, f"Job ID mismatch: expected {job_id}, got {data['jobId']}"
        
        # Check status is valid
        valid_statuses = ["queued", "running", "done", "failed"]
        if data["status"] not in valid_statuses:
            return False, f"Invalid status: {data['status']}"
        
        # Check stats structure
        stats = data["stats"]
        if not isinstance(stats, dict):
            return False, "Stats should be a dictionary"
        
        return True, f"Job status retrieved: {data['status']} at {data['percent']}%"
        
    except Exception as e:
        return False, f"Request failed: {str(e)}"

def test_job_tables(job_id: str):
    """Test GET /api/jobs/{job_id}/tables endpoint"""
    try:
        # Wait for job to progress and create tables
        time.sleep(5)
        
        response = requests.get(f"{BACKEND_URL}/jobs/{job_id}/tables", timeout=10)
        
        if response.status_code != 200:
            return False, f"HTTP {response.status_code}: {response.text}"
        
        data = response.json()
        
        if "tables" not in data:
            return False, "Missing 'tables' field in response"
        
        tables = data["tables"]
        if not isinstance(tables, list):
            return False, "Tables should be a list"
        
        # Check for demo tables (should have Northwind demo tables)
        expected_demo_tables = ["Customers", "Orders", "Products", "Categories", "Employees"]
        found_tables = [table["name"] for table in tables if "name" in table]
        
        demo_tables_found = 0
        for expected_table in expected_demo_tables:
            if expected_table in found_tables:
                demo_tables_found += 1
        
        if demo_tables_found == 0:
            return False, f"No demo tables found. Found tables: {found_tables}"
        
        # Check table structure
        for table in tables:
            required_table_fields = ["schema", "name", "rowCount"]
            for field in required_table_fields:
                if field not in table:
                    return False, f"Missing field '{field}' in table: {table}"
        
        return True, f"Found {len(tables)} tables, {demo_tables_found} demo tables identified"
        
    except Exception as e:
        return False, f"Request failed: {str(e)}"

def wait_for_job_completion(job_id: str, max_wait_seconds: int = 60):
    """Wait for job to complete and return final status"""
    start_time = time.time()
    
    while time.time() - start_time < max_wait_seconds:
        try:
            response = requests.get(f"{BACKEND_URL}/jobs/{job_id}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                percent = data.get("percent", 0)
                
                print(f"Job progress: {status} - {percent}%")
                
                if status in ["done", "failed"]:
                    return status, data
                
            time.sleep(3)
        except Exception as e:
            print(f"Error checking job status: {e}")
            time.sleep(3)
    
    return "timeout", None

def run_all_tests():
    """Run all backend tests"""
    result = TestResult()
    
    print("🚀 Starting Backend Tests for Demo Migration")
    print(f"Backend URL: {BACKEND_URL}")
    print("="*60)
    
    # Test 1: API Health Check
    print("\n1. Testing API Health...")
    success, message = test_api_health()
    if success:
        result.add_pass("API Health Check")
    else:
        result.add_fail("API Health Check", message)
        return result  # Stop if API is not accessible
    
    # Test 2: Demo Migration Start
    print("\n2. Testing Demo Migration Start...")
    success, message, job_id = test_demo_migration_start()
    if success:
        result.add_pass("Demo Migration Start")
        print(f"   Job ID: {job_id}")
    else:
        result.add_fail("Demo Migration Start", message)
        return result  # Stop if can't start demo
    
    # Test 3: Job Status Check
    print("\n3. Testing Job Status Retrieval...")
    success, message = test_job_status(job_id)
    if success:
        result.add_pass("Job Status Retrieval")
        print(f"   {message}")
    else:
        result.add_fail("Job Status Retrieval", message)
    
    # Test 4: Job Tables Check
    print("\n4. Testing Job Tables Retrieval...")
    success, message = test_job_tables(job_id)
    if success:
        result.add_pass("Job Tables Retrieval")
        print(f"   {message}")
    else:
        result.add_fail("Job Tables Retrieval", message)
    
    # Test 5: Wait for Job Completion
    print("\n5. Waiting for Job Completion...")
    final_status, final_data = wait_for_job_completion(job_id, max_wait_seconds=90)
    
    if final_status == "done":
        result.add_pass("Job Completion")
        print(f"   Job completed successfully in {final_data.get('stats', {}).get('elapsedSec', 'unknown')} seconds")
    elif final_status == "failed":
        error_msg = final_data.get('error', 'Unknown error') if final_data else 'Unknown error'
        result.add_fail("Job Completion", f"Job failed: {error_msg}")
    elif final_status == "timeout":
        result.add_fail("Job Completion", "Job did not complete within timeout period")
    else:
        result.add_fail("Job Completion", f"Unexpected final status: {final_status}")
    
    return result

if __name__ == "__main__":
    print("MSSQL BAK to PostgreSQL Migration Tool - Backend Tests")
    print("Testing Demo Migration Functionality")
    
    result = run_all_tests()
    success = result.summary()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)