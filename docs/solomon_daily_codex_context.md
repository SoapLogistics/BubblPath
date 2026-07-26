# Daily Operating Rhythm

## Morning

- Refresh status.
- Run quick tests.
- Review blockers.
- Choose one packet.

## During work

- Keep scope small.
- Update tests with behavior.
- Avoid unrelated cleanup.
- Record blockers immediately.

## End of cycle

- Run verification.
- Write memory.
- Update context pack.
- Propose next safe step.


## Futures Daily Scan Output
```json
[
  {
    "target_id": "match_001",
    "confidence": 91.5,
    "threshold_80_met": true,
    "threshold_90_met": true,
    "data_health": "verified",
    "payload": {
      "type": "daily_scan"
    },
    "timestamp": 1785084503.5989246
  },
  {
    "target_id": "match_002",
    "confidence": 80.1,
    "threshold_80_met": true,
    "threshold_90_met": false,
    "data_health": "verified",
    "payload": {
      "type": "daily_scan"
    },
    "timestamp": 1785084503.598962
  },
  {
    "target_id": "match_003",
    "confidence": 75.0,
    "threshold_80_met": false,
    "threshold_90_met": false,
    "data_health": "marginal",
    "payload": {
      "type": "daily_scan"
    },
    "timestamp": 1785084503.5989645
  }
]
```
