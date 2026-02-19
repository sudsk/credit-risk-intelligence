#!/usr/bin/env python3
"""
MCP Servers Runner - Local Development
Starts all 6 MCP servers as separate processes for local testing.

For production Cloud Run deployment, each server runs independently.
"""
import subprocess
import sys
import time
import signal
from pathlib import Path

# Get the data_sources directory
DATA_SOURCES_DIR = Path(__file__).parent / "data_sources"

# MCP servers to run
SERVERS = [
    {
        "name": "Companies House",
        "file": "companies_house_server.py",
        "port": 8001,
        "description": "Company registration and compliance data"
    },
    {
        "name": "Financial Data",
        "file": "financial_server.py",
        "port": 8002,
        "description": "Financial metrics and ratios"
    },
    {
        "name": "LinkedIn Data",
        "file": "linkedin_server.py",
        "port": 8003,
        "description": "Employee count and hiring trends"
    },
    {
        "name": "News Intelligence",
        "file": "news_server.py",
        "port": 8004,
        "description": "News events and sentiment analysis"
    },
    {
        "name": "Payment Data",
        "file": "payment_data_server.py",
        "port": 8005,
        "description": "Payment behavior and transaction volume"
    },
    {
        "name": "Web Traffic",
        "file": "web_traffic_server.py",
        "port": 8006,
        "description": "Website traffic and engagement metrics"
    }
]

processes = []

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\n🛑 Shutting down all MCP servers...")
    for proc in processes:
        proc.terminate()
    print("✅ All servers stopped\n")
    sys.exit(0)

def main():
    """Start all MCP servers"""
    print("=" * 70)
    print("🚀 STARTING FORESIGHT AI MCP SERVERS")
    print("=" * 70)
    print()
    
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start each server
    for server in SERVERS:
        server_path = DATA_SOURCES_DIR / server["file"]
        
        if not server_path.exists():
            print(f"❌ ERROR: {server['file']} not found at {server_path}")
            continue
        
        print(f"✓ Starting {server['name']}...")
        print(f"  - Port: {server['port']}")
        print(f"  - Description: {server['description']}")
        print(f"  - URL: http://localhost:{server['port']}")
        
        # Start the server process
        proc = subprocess.Popen(
            [sys.executable, str(server_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**dict(os.environ), "PORT": str(server["port"])}
        )
        processes.append(proc)
        print()
    
    print("=" * 70)
    print(f"✅ ALL {len(SERVERS)} MCP SERVERS RUNNING!")
    print("=" * 70)
    print()
    print("📡 Server Endpoints:")
    for server in SERVERS:
        print(f"   • {server['name']:<20} http://localhost:{server['port']}")
    print()
    print("🔧 ADK Agents Configuration:")
    print("   Update agents/shared/config.py with these URLs")
    print()
    print("⚠️  Press Ctrl+C to stop all servers")
    print("=" * 70)
    print()
    
    # Keep the main process running
    try:
        while True:
            time.sleep(1)
            # Check if any process died
            for i, proc in enumerate(processes):
                if proc.poll() is not None:
                    server = SERVERS[i]
                    print(f"\n❌ WARNING: {server['name']} server stopped unexpectedly")
                    print(f"   Check logs for {server['file']}")
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    import os
    main()