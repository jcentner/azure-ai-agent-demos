#!/usr/bin/env python3
"""Test MCP connection and GitHub PAT independently."""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_github_pat():
    """Test if the GitHub PAT is valid."""
    pat = os.getenv("GITHUB_PAT")
    if not pat:
        print("❌ No GITHUB_PAT found in environment")
        return False
    
    # Test the PAT with GitHub API
    response = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {pat}"}
    )
    
    if response.status_code == 200:
        user = response.json()
        print(f"✅ GitHub PAT is valid (user: {user.get('login', 'unknown')})")
        
        # Check rate limit
        rate_limit = requests.get(
            "https://api.github.com/rate_limit",
            headers={"Authorization": f"Bearer {pat}"}
        ).json()
        remaining = rate_limit.get('rate', {}).get('remaining', 'unknown')
        print(f"   Rate limit remaining: {remaining}")
        return True
    else:
        print(f"❌ GitHub PAT test failed: {response.status_code} - {response.text}")
        return False

def test_mcp_server():
    """Test if the MCP server is reachable."""
    # Note: The GitHub MCP server might require proper MCP protocol handshake
    # This is just a basic connectivity test
    response = requests.get("https://api.githubcopilot.com/mcp/")
    print(f"MCP server response: {response.status_code}")
    if response.status_code < 500:
        print("✅ MCP server is reachable")
    else:
        print("⚠️ MCP server returned error")

if __name__ == "__main__":
    print("Testing GitHub PAT...")
    test_github_pat()
    print("\nTesting MCP server connectivity...")
    test_mcp_server()