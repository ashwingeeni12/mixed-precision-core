"""
Quick test of new hardware metrics - runs 1 case only
"""
import os
os.environ['QUICK_TEST'] = 'true'
os.environ['MAX_CASES'] = '1'

import run_comprehensive_test
run_comprehensive_test.main()
