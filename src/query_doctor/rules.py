RULES = [
    {
        "rule_id": "QDOC-INDEX-001",
        "title": "Possible missing index",
        "severity": "HIGH",
        "description": "Sequential scans with heavy filtering may warrant a supporting index.",
    },
    {
        "rule_id": "QDOC-SCAN-001",
        "title": "Sequential scan risk",
        "severity": "MEDIUM",
        "description": (
            "Large scans with limited output can still be expensive depending on "
            "table size and query shape."
        ),
    },
    {
        "rule_id": "QDOC-JOIN-001",
        "title": "Nested loop risk",
        "severity": "MEDIUM",
        "description": (
            "Large nested loops can amplify runtime when the inner side is expensive or repeated."
        ),
    },
    {
        "rule_id": "QDOC-JOIN-002",
        "title": "Join efficiency",
        "severity": "LOW",
        "description": (
            "High row counts or repeated work on join nodes may indicate suboptimal join choices."
        ),
    },
    {
        "rule_id": "QDOC-ESTIMATE-001",
        "title": "Cardinality estimation mismatch",
        "severity": "MEDIUM",
        "description": (
            "Large planned-vs-actual row mismatches can indicate stale statistics or skewed data."
        ),
    },
    {
        "rule_id": "QDOC-FILTER-001",
        "title": "Rows removed by filter",
        "severity": "LOW",
        "description": (
            "A large share of rows rejected by predicate may be a sign of poor "
            "selectivity or an opportunity to improve access paths."
        ),
    },
    {
        "rule_id": "QDOC-SORT-001",
        "title": "Expensive sort",
        "severity": "MEDIUM",
        "description": (
            "Sorting a large number of rows can dominate runtime, especially "
            "with external disk-based sorts."
        ),
    },
    {
        "rule_id": "QDOC-SPILL-001",
        "title": "Disk spill observed",
        "severity": "MEDIUM",
        "description": (
            "In-memory sort work spilling to disk can indicate memory pressure "
            "or a larger-than-expected sort."
        ),
    },
    {
        "rule_id": "QDOC-PERF-001",
        "title": "Expensive node",
        "severity": "LOW",
        "description": (
            "A plan node is taking unusually long relative to the configured threshold."
        ),
    },
]
