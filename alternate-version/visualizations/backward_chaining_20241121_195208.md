# Backward Chaining Visualization

Generated: 2024-11-21 19:52:08

## Knowledge Base
```
TELL
p2=> p3; p3 => p1; c => e; b&e => f; f&g => h; p2&p1&p3 =>d; p1&p3 => c; a; b; p2;

ASK
d
```

## Inference Process

```mermaid
graph RL
    Goal[Query<br/>d]
    N0[Need<br/>6] -->|Requires| Goal
    N1[Need<br/>5] -->|Requires| N0
    N2[Need<br/>4] -->|Requires| N1
    N3[Need<br/>3] -->|Requires| N2
    N4[Need<br/>2] -->|Requires| N3
    N5[Need<br/>1] -->|Requires| N4
    N6[Need<br/>0] -->|Requires| N5
```

### Reasoning Chain

**Step 1:**
- Attempting to prove: p2 AND p1 AND p3 => d

**Step 2:**
- Found fact: p2

**Step 3:**
- Attempting to prove: p3 => p1

**Step 4:**
- Attempting to prove: p2 => p3

**Step 5:**
- Found fact: p2

**Step 6:**
- Attempting to prove: p2 => p3

**Step 7:**
- Found fact: p2