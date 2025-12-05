# Logging System Architecture

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    User runs script.py                      │
│         python scripts/script.py --dir ./files              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │   Check --no-logs flag?       │
         └───────┬───────────────┬───────┘
                 │               │
            No   │               │ Yes
                 │               │
                 ▼               ▼
    ┌────────────────────┐   ┌──────────────────┐
    │  setup_logger()    │   │  Skip logging    │
    │  Redirect stdout   │   │  Run normally    │
    └─────────┬──────────┘   └──────────────────┘
              │
              ▼
    ┌─────────────────────────────────────┐
    │  All print() calls captured to:     │
    │  1. Terminal (user sees output)     │
    │  2. Log buffer (stored in memory)   │
    └─────────────────┬───────────────────┘
                      │
                      ▼
    ┌─────────────────────────────────────┐
    │    Script execution completes       │
    │    (success or error)               │
    └─────────────────┬───────────────────┘
                      │
                      ▼
         ┌────────────────────────────────┐
         │  Check --auto-save-logs flag?  │
         └────────┬──────────────┬────────┘
                  │              │
             No   │              │ Yes
                  │              │
                  ▼              ▼
    ┌──────────────────────┐  ┌─────────────────────┐
    │  Prompt user:        │  │  Auto-save with     │
    │  "Save logs? (y/n)"  │  │  timestamp          │
    └──────┬───────────────┘  └──────────┬──────────┘
           │                              │
           ▼                              │
    ┌──────────────┐                     │
    │  User says   │                     │
    │  'y' or 'n'? │                     │
    └──┬───────┬───┘                     │
       │       │                         │
    y  │       │ n                       │
       │       │                         │
       ▼       ▼                         │
    ┌────┐  ┌────────┐                  │
    │Save│  │Discard │                  │
    └─┬──┘  └────────┘                  │
      │                                  │
      ▼                                  │
    ┌──────────────────────┐            │
    │ Prompt for filename  │            │
    │ (or use timestamp)   │            │
    └──────────┬───────────┘            │
               │                         │
               ▼                         ▼
    ┌──────────────────────────────────────────┐
    │  Save to logs/run_YYYYMMDD_HHMMSS.log   │
    │  or logs/custom_name.log                 │
    └──────────────────────────────────────────┘
```

## Component Interaction

```
┌─────────────────────────────────────────────────────────────┐
│                        script.py                            │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Main Execution                                     │    │
│  │  • Parse arguments                                  │    │
│  │  • Setup logger (if enabled)                        │    │
│  │  • Run file processing                              │    │
│  │  • Handle log saving (finally block)                │    │
│  └────────────────────────────────────────────────────┘    │
└───────────────────────┬─────────────────────────────────────┘
                        │ imports
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                       logger.py                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Logger Class                                       │    │
│  │  • write(message) → terminal + buffer               │    │
│  │  • get_logs() → return all buffered logs            │    │
│  │  • save_logs(filename) → write to file              │    │
│  │  • Thread-safe with locks                           │    │
│  └────────────────────────────────────────────────────┘    │
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Helper Functions                                   │    │
│  │  • setup_logger() → initialize & redirect stdout    │    │
│  │  • get_logger() → get global instance               │    │
│  │  • restore_stdout() → restore original stdout       │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    File System                              │
│  FileSense/                                                 │
│  └── logs/                                                  │
│      ├── run_20251205_143022.log                           │
│      ├── run_20251205_145930.log                           │
│      └── custom_name.log                                   │
└─────────────────────────────────────────────────────────────┘
```

## Thread Safety

```
┌─────────────────────────────────────────────────────────────┐
│                    Multi-threaded Processing                │
│                                                             │
│  Thread 1: process_file("doc1.pdf")                        │
│     │                                                       │
│     └──► print("Processing doc1...") ──┐                   │
│                                         │                   │
│  Thread 2: process_file("doc2.pdf")    │                   │
│     │                                   │                   │
│     └──► print("Processing doc2...") ──┤                   │
│                                         │                   │
│  Thread 3: process_file("doc3.pdf")    │                   │
│     │                                   │                   │
│     └──► print("Processing doc3...") ──┤                   │
│                                         │                   │
│                                         ▼                   │
│                              ┌──────────────────┐          │
│                              │  Logger.write()  │          │
│                              │  with lock:      │          │
│                              │    buffer.append │          │
│                              └──────────────────┘          │
│                                         │                   │
│                                         ▼                   │
│                              ┌──────────────────┐          │
│                              │  Synchronized    │          │
│                              │  Log Buffer      │          │
│                              └──────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

```
User Input (print statement)
    │
    ▼
sys.stdout.write() → Logger.write()
    │                      │
    │                      ├──► Terminal (immediate display)
    │                      │
    │                      └──► Log Buffer (with lock)
    │                              │
    │                              │ (stored in memory)
    │                              │
    ▼                              ▼
Script completes              User prompted
    │                              │
    │                              ▼
    │                         Save to file?
    │                              │
    │                              ▼
    └──────────────────────► logs/filename.log
```
