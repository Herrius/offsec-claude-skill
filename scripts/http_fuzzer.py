#!/usr/bin/env python3
"""
Simple HTTP Parameter Fuzzer
Usage: python3 http_fuzzer.py <url> <wordlist> <param_name>
"""

import requests
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin

def test_parameter(url, param_name, value, method='GET'):
    """
    Test a single parameter value.
    Returns (value, status_code, length) if interesting.
    """
    try:
        if method.upper() == 'GET':
            params = {param_name: value}
            response = requests.get(url, params=params, timeout=5, allow_redirects=False)
        else:
            data = {param_name: value}
            response = requests.post(url, data=data, timeout=5, allow_redirects=False)

        return {
            'value': value,
            'status': response.status_code,
            'length': len(response.content),
            'response': response
        }
    except requests.exceptions.RequestException as e:
        return None

def fuzz_parameter(url, param_name, wordlist_path, method='GET', threads=20):
    """
    Fuzz a parameter with values from a wordlist.
    """
    print(f"[*] Starting HTTP fuzzer")
    print(f"[*] Target: {url}")
    print(f"[*] Parameter: {param_name}")
    print(f"[*] Method: {method}")
    print(f"[*] Wordlist: {wordlist_path}")
    print("-" * 70)

    # Load wordlist
    try:
        with open(wordlist_path, 'r') as f:
            payloads = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[-] Error: Wordlist file not found: {wordlist_path}")
        sys.exit(1)

    print(f"[*] Loaded {len(payloads)} payloads")
    print(f"[*] Starting fuzzing...\n")

    results = []
    baseline_length = None

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {
            executor.submit(test_parameter, url, param_name, payload, method): payload
            for payload in payloads
        }

        for future in as_completed(futures):
            result = future.result()
            if result:
                # Set baseline on first result
                if baseline_length is None:
                    baseline_length = result['length']

                # Print interesting results (different status or length)
                if result['status'] != 404 or result['length'] != baseline_length:
                    print(f"[+] {result['value']:<30} Status: {result['status']:<3} Length: {result['length']}")
                    results.append(result)

    print("\n" + "-" * 70)
    print(f"[*] Fuzzing complete")
    print(f"[*] Found {len(results)} interesting responses")

    return results

def main():
    if len(sys.argv) < 4:
        print(f"Usage: {sys.argv[0]} <url> <wordlist> <param_name> [method]")
        print(f"Example: {sys.argv[0]} http://target.com/search wordlist.txt q GET")
        print(f"         {sys.argv[0]} http://target.com/login wordlist.txt username POST")
        sys.exit(1)

    url = sys.argv[1]
    wordlist = sys.argv[2]
    param_name = sys.argv[3]
    method = sys.argv[4] if len(sys.argv) > 4 else 'GET'

    # Run fuzzing
    results = fuzz_parameter(url, param_name, wordlist, method)

    # Save results
    if results:
        output_file = "fuzzing_results.txt"
        with open(output_file, 'w') as f:
            for result in results:
                f.write(f"{result['value']},{result['status']},{result['length']}\n")
        print(f"\n[*] Results saved to: {output_file}")

if __name__ == "__main__":
    main()
