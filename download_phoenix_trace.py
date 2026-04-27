#!/usr/bin/env python3
"""Download the last trace from Phoenix."""

import requests
import json
import sys

# Phoenix GraphQL endpoint
PHOENIX_URL = "http://localhost:6006/graphql"

# Query to get the most recent trace
query = """
query GetTraces {
  traces(first: 1, sort: {col: startTime, dir: desc}) {
    edges {
      node {
        traceId
        projectId
        startTime
        endTime
        latencyMs
        tokenCountTotal
        tokenCountPrompt
        tokenCountCompletion
      }
    }
  }
}
"""

def get_latest_trace():
    """Get the latest trace from Phoenix."""
    response = requests.post(
        PHOENIX_URL,
        json={"query": query},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        print(f"Error: HTTP {response.status_code}")
        print(response.text)
        return None
    
    data = response.json()
    
    if "errors" in data:
        print("GraphQL Errors:")
        print(json.dumps(data["errors"], indent=2))
        return None
    
    traces = data.get("data", {}).get("traces", {}).get("edges", [])
    
    if not traces:
        print("No traces found")
        return None
    
    return traces[0]["node"]

def get_trace_details(trace_id):
    """Get detailed information about a specific trace."""
    detail_query = f"""
    query GetTrace {{
      trace(traceId: "{trace_id}") {{
        traceId
        projectId
        startTime
        endTime
        latencyMs
        tokenCountTotal
        tokenCountPrompt
        tokenCountCompletion
        spans {{
          spanId
          name
          spanKind
          startTime
          endTime
          latencyMs
          statusCode
          statusMessage
          attributes
          events
        }}
      }}
    }}
    """
    
    response = requests.post(
        PHOENIX_URL,
        json={"query": detail_query},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        print(f"Error: HTTP {response.status_code}")
        print(response.text)
        return None
    
    data = response.json()
    
    if "errors" in data:
        print("GraphQL Errors:")
        print(json.dumps(data["errors"], indent=2))
        return None
    
    return data.get("data", {}).get("trace")

def main():
    print("Fetching latest trace from Phoenix...")
    
    # Get the latest trace
    latest_trace = get_latest_trace()
    
    if not latest_trace:
        sys.exit(1)
    
    print(f"\nLatest Trace ID: {latest_trace['traceId']}")
    print(f"Start Time: {latest_trace['startTime']}")
    print(f"End Time: {latest_trace['endTime']}")
    print(f"Latency: {latest_trace.get('latencyMs', 'N/A')} ms")
    
    # Get detailed trace information
    print(f"\nFetching detailed trace information...")
    trace_details = get_trace_details(latest_trace['traceId'])
    
    if trace_details:
        # Save to file
        output_file = f"trace_{latest_trace['traceId']}.json"
        with open(output_file, 'w') as f:
            json.dump(trace_details, f, indent=2)
        
        print(f"\nTrace saved to: {output_file}")
        print(f"Number of spans: {len(trace_details.get('spans', []))}")
    else:
        print("Failed to fetch trace details")
        sys.exit(1)

if __name__ == "__main__":
    main()

# Made with Bob
