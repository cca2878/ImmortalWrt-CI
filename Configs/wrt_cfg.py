#!/usr/bin/env python3
"""
Helper to read values from a WRT-CONTAINER config YAML file.

Usage:
  wrt_cfg.py get <yml_file> <key> [<subkey> ...]   -- print a scalar value
  wrt_cfg.py hook <yml_file> <hook_name>           -- print hook script content
"""
import sys
import yaml

cmd = sys.argv[1]
yml_file = sys.argv[2]

try:
    with open(yml_file) as f:
        cfg = yaml.safe_load(f) or {}
except (FileNotFoundError, yaml.YAMLError):
    cfg = {}

if cmd == 'get':
    val = cfg
    for k in sys.argv[3:]:
        val = (val if isinstance(val, dict) else {}).get(k) or ''
    print(val if isinstance(val, str) else '', end='')

elif cmd == 'hook':
    script = ((cfg.get('hooks') or {}).get(sys.argv[3]) or '').strip()
    print(script, end='')
