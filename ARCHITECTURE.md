# Architecture Overview

## Core Concepts
- LogEntry: structured representation of a log line
- Checker: independent rule that analyzes log entries
- Finding: standardized output of anomalies

## Data Flow
Log file → LogEntry → Checker(s) → Finding(s) → Report

## Checker Design
- Checkers are independent and composable
- Each checker may maintain internal state
- Checkers return zero or more Findings
