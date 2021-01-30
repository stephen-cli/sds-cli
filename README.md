# Synology DiskStation CLI

A CLI that can be used to interact with a Synology NAS on your network.

## Usage
```
python main.py [--username USERNAME] address
```

_e.g._
```
python main.py 192.168.1.111:5000
```

## Download Station Commands
---
### info
Returns Download Station info

---
### get-config
Returns Download Station config

---
### get-tasks
Provides task listing and detailed task information

#### Options
```
  [--id <value>]
     Task IDs, separated by ",". Cannot be used with --offset or --limit.
  [--offset <value>]
     Beginning task on the request record. Default to "0". Cannot be used with --id.
  [--limit <value>]
     Number of records requested. Default to list all tasks. Cannot be used with --id.
  [--detail]
  [--transfer]
```
---