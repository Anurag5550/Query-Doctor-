# Heuristics

Query Doctor uses conservative, evidence-based heuristics. The goal is not to assert a guaranteed root cause from a plan alone but to draw attention to patterns that often deserve investigation.

## QDOC-INDEX-001 — Possible missing index

This rule is triggered when a sequential scan is reading a large number of rows and filtering out almost all of them before returning a relatively small result set. The rule looks for:

- a `Seq Scan` node,
- a filter or predicate,
- large `Rows Removed by Filter`,
- a small actual row count relative to the amount of work performed.

The recommendation is phrased as a possibility, not a certainty. The tool may suggest a candidate like `orders(customer_id)` without declaring that a specific index is the solution.

## QDOC-SCAN-001 — Sequential scan risk

A `Seq Scan` is not automatically bad. This rule only raises a signal when the scan is expensive enough or wasteful enough that it may warrant investigation. For example, a small table with a single row read is not suspicious. A large table that reads a lot of rows and filters most of them may be.

## QDOC-JOIN-001 — Nested loop risk

Nested loops are common and can be excellent when the inner side is selective. This rule focuses on repeated or heavy nested loop patterns with substantial runtime, especially when the inner side is executed many times.

The message explains the risk without saying a nested loop is inherently wrong.

## QDOC-JOIN-002 — Join efficiency

This rule looks for join nodes with substantial row counts or runtime. It raises a lower-confidence signal when the planner might be doing a lot of expensive join work or choosing a less useful access pattern for the available data distribution.

## QDOC-ESTIMATE-001 — Cardinality estimation mismatch

This rule compares planned rows to actual rows and flags large mismatches. It does not blame a single cause. Instead, it suggests stale statistics, skewed data, correlated predicates, or other estimator limitations as reasonable possibilities.

## QDOC-FILTER-001 — Rows removed by filter

If a plan is throwing away thousands of rows after reading a large dataset, that is often materially useful context. It can indicate a predicate with poor selectivity or a value that would benefit from an index or better access path.

## QDOC-SORT-001 — Expensive sort

Sort nodes become more suspicious when they process a large number of rows and take a meaningful share of total execution time. The rule is sensitive to sort size and actual runtime.

## QDOC-SPILL-001 — Disk spill observed

A sort that uses an external merge or indicates disk activity may be spilling to temporary storage. This can be a sign of memory pressure or a larger-than-expected working set. The recommendation calls for investigation rather than a direct memory increase recommendation.

## QDOC-PERF-001 — Expensive node

This rule watches for plan nodes that cross a user-configurable time threshold. It is a general-purpose signal for top-level expensive nodes that deserve context.
