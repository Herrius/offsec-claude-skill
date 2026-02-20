#!/usr/bin/env python3
"""
Simple Subdomain Enumeration Tool
Usage: python3 subdomain_enum.py <domain> <wordlist>
"""

import dns.resolver
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

def check_subdomain(subdomain, domain):
    """
    Check if a subdomain exists and return its IP addresses.
    """
    full_domain = f"{subdomain}.{domain}"
    try:
        answers = dns.resolver.resolve(full_domain, 'A')
        ips = [str(answer) for answer in answers]
        return (full_domain, ips)
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
        return None
    except Exception as e:
        return None

def enumerate_subdomains(domain, wordlist_path, threads=50):
    """
    Enumerate subdomains using a wordlist.
    """
    print(f"[*] Starting subdomain enumeration for {domain}")
    print(f"[*] Using wordlist: {wordlist_path}")
    print("-" * 70)

    found_subdomains = []

    try:
        with open(wordlist_path, 'r') as f:
            subdomains = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[-] Error: Wordlist file not found: {wordlist_path}")
        sys.exit(1)

    print(f"[*] Loaded {len(subdomains)} potential subdomains")
    print(f"[*] Starting enumeration...\n")

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {
            executor.submit(check_subdomain, sub, domain): sub
            for sub in subdomains
        }

        for future in as_completed(futures):
            result = future.result()
            if result:
                full_domain, ips = result
                print(f"[+] Found: {full_domain} -> {', '.join(ips)}")
                found_subdomains.append((full_domain, ips))

    print("\n" + "-" * 70)
    print(f"[*] Enumeration complete")
    print(f"[*] Found {len(found_subdomains)} subdomains")

    return found_subdomains

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <domain> <wordlist>")
        print(f"Example: {sys.argv[0]} example.com subdomains.txt")
        sys.exit(1)

    domain = sys.argv[1]
    wordlist = sys.argv[2]

    # Run enumeration
    found = enumerate_subdomains(domain, wordlist)

    # Save results
    if found:
        output_file = f"{domain}_subdomains.txt"
        with open(output_file, 'w') as f:
            for subdomain, ips in found:
                f.write(f"{subdomain},{','.join(ips)}\n")
        print(f"\n[*] Results saved to: {output_file}")

if __name__ == "__main__":
    main()
