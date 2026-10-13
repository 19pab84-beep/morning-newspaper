#!/usr/bin/env python3
"""Compatibility entry point for the V3 REVIEW generator.

The retired hard-coded 4×4/template renderer has been removed. An input
manuscript and an external private store are now mandatory, just as in v3.build.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from v3.build import main

if __name__=='__main__':
    main()
