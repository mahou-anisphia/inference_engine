# Forward Chaining Visualization

Generated: 2024-11-21 19:48:29

## Knowledge Base
```
TELL
p2=> p3; p3 => p1; c => e; b&e => f; f&g => h; p2&p1&p3 =>d; p1&p3 => c; a; b; p2;

ASK
d
```

## Inference Process

```mermaid
flowchart TD
    A[Initial Facts: , a, b, p2]
    A -->|Step 1| B1[Added: p3]
    A -->|Step 2| B2[Added: p1]
    A -->|Step 3| B3[Added: c, d]
    A -->|Step 4| B4[Added: e]
    A -->|Step 5| B5[Added: f]
```

### Step-by-Step Explanation

**Step 1:**
- Previous facts: , a, b, p2
- New facts derived: p3

**Step 2:**
- Previous facts: , a, b, p2, p3
- New facts derived: p1

**Step 3:**
- Previous facts: , a, b, p1, p2, p3
- New facts derived: c, d

**Step 4:**
- Previous facts: , a, b, c, d, p1, p2, p3
- New facts derived: e

**Step 5:**
- Previous facts: , a, b, c, d, e, p1, p2, p3
- New facts derived: f