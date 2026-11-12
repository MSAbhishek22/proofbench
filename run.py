#!/usr/bin/env python3
"""ProofBench entry point: python3 run.py [port]"""
import sys

from app.server import main

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8773
    main(port=port)
