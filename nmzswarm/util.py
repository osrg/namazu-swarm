"""util
"""
import json
from typing import Any, Dict, List


def parse_json(b: bytes) -> Dict[str, Any]:
    """parse json bytes"""
    return json.loads(b.decode('utf-8'))


def parse_jsonl(b: bytes) -> List[Dict[str, Any]]:
    """parse jsonl bytes"""
    return [parse_json(x) for x in b.splitlines()]
