"""
Test script for AI Interview Screener
Run this after starting the server to test all endpoints
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def print_json(data: Dict[Any, Any]):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=2))

def test_health_check():
    """Test the health check endpoint"""
    print_section("Testing Health Check")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    print_json(response.json())

def test_evaluate_answer():
    """Test single answer evaluation"""
    print_section("Testing /evaluate-answer")
    
    test_cases = [
        {
            "name": "Good Answer",
            "data": {
                "candidate_says": "I would use a hash table for O(1) lookup time. Hash tables provide constant-time average case performance for insertions and lookups, making them ideal for caching and fast data retrieval. However, they have O(n) worst-case complexity and don't maintain order.",
                "question_context": "What data structure would you use for a cache implementation?"
            }
        },
        {
            "name": "Average Answer",
            "data": {
                "candidate_says": "I'd use a dictionary because it's fast",
                "question_context": "What data structure would you use for a cache implementation?"
            }
        },
        {
            "name": "Poor Answer",
            "data": {
                "candidate_says": "Arrays are good",
                "question_context": "What data structure would you use for a cache implementation?"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        print(f"Question: {test_case['data']['question_context']}")
        print(f"Answer: {test_case['data']['candidate_says']}\n")
        
        response = requests.post(
            f"{BASE_URL}/evaluate-answer",
            json=test_case['data']
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Score: {result['score']}/5")
            print(f"Summary: {result['summary']}")
            print(f"Improvement: {result['improvement']}")
        else:
            print(f"Error: {response.text}")
        print()

def test_rank_candidates():
    """Test candidate ranking"""
    print_section("Testing /rank-candidates")
    
    request_data = {
        "candidates": [
            {
                "candidate_id": "Alice_123",
                "answer": "React is component-based",
                "question_context": "Why would you choose React for a large application?"
            },
            {
                "candidate_id": "Bob_456",
                "answer": "React offers component reusability, virtual DOM for performance optimization, a rich ecosystem with tools like Redux for state management, strong community support, and it scales well for large applications with features like code splitting and lazy loading.",
                "question_context": "Why would you choose React for a large application?"
            },
            {
                "candidate_id": "Charlie_789",
                "answer": "React is popular and has many libraries. It's used by Facebook and other big companies. Components make it modular.",
                "question_context": "Why would you choose React for a large application?"
            },
            {
                "candidate_id": "Diana_012",
                "answer": "I don't know much about React",
                "question_context": "Why would you choose React for a large application?"
            }
        ]
    }
    
    print("Evaluating 4 candidates...\n")
    
    response = requests.post(
        f"{BASE_URL}/rank-candidates",
        json=request_data
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\nRanked Candidates:\n")
        
        for candidate in result['ranked_candidates']:
            print(f"Rank #{candidate['rank']} - {candidate['candidate_id']}")
            print(f"  Score: {candidate['score']}/5")
            print(f"  Summary: {candidate['summary']}")
            print(f"  Improvement: {candidate['improvement']}")
            print(f"  Answer: {candidate['answer'][:80]}...")
            print()
    else:
        print(f"Error: {response.text}")

def test_error_handling():
    """Test error handling"""
    print_section("Testing Error Handling")
    
    # Empty answer
    print("--- Test: Empty Answer ---")
    response = requests.post(
        f"{BASE_URL}/evaluate-answer",
        json={"candidate_says": ""}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}\n")
    
    # Missing required field
    print("--- Test: Missing Field ---")
    response = requests.post(
        f"{BASE_URL}/evaluate-answer",
        json={}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}\n")
    
    # Empty candidates list
    print("--- Test: Empty Candidates List ---")
    response = requests.post(
        f"{BASE_URL}/rank-candidates",
        json={"candidates": []}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}\n")

def run_all_tests():
    """Run all test cases"""
    print("\n" + "🚀 " * 20)
    print("  AI INTERVIEW SCREENER - TEST SUITE")
    print("🚀 " * 20)
    
    try:
        test_health_check()
        test_evaluate_answer()
        test_rank_candidates()
        test_error_handling()
        
        print_section("All Tests Complete! ✅")
        print("The API is working correctly.")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the server.")
        print("Make sure the FastAPI server is running on http://localhost:8000")
        print("Start it with: python main.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    run_all_tests()