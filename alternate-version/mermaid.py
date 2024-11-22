import os
from datetime import datetime


class InferenceEngine:
    def __init__(self):
        self.kb = []
        self.facts = set()
        self.rules = []
        self.visualize = True

    def parse_kb(self, tell_string):
        clauses = tell_string.split(';')
        for clause in clauses:
            clause = clause.strip()
            if '=>' in clause:
                premise, conclusion = clause.split('=>')
                self.rules.append((premise.strip(), conclusion.strip()))
            else:
                self.facts.add(clause)

    def generate_fc_diagram(self, steps, kb_str, query):
        """Generate Markdown content for Forward Chaining steps with linear visualization"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        md_content = [
            "# Forward Chaining Visualization",
            f"\nGenerated: {timestamp}",
            "\n## Knowledge Base",
            f"```\nTELL\n{kb_str}\n\nASK\n{query}\n```",
            "\n## Inference Process\n",
            "```mermaid",
            "graph LR"  # Changed to LR for left-to-right linear flow
        ]

        # Add initial facts node
        md_content.append(
            f"    Start[Initial Facts<br/>{', '.join(sorted(steps[0]))}]")

        # Add each step in a linear chain
        prev_node = "Start"
        for i in range(1, len(steps)):
            prev_facts = steps[i-1]
            new_facts = steps[i].difference(prev_facts)
            if new_facts:
                node_id = f"Step{i}"
                # Show only the new facts at each step
                md_content.append(
                    f"    {prev_node} -->|Apply Rules| {node_id}[Step {i}<br/>Added: {', '.join(sorted(new_facts))}]")
                prev_node = node_id

        # Add final result node if query was found
        if query in steps[-1]:
            md_content.append(
                f"    {prev_node} -->|Found| Result[Query '{query}'<br/>PROVEN]")

        md_content.append("```\n")

        # Add explanation
        md_content.append("### Step-by-Step Explanation")
        for i in range(1, len(steps)):
            prev_facts = steps[i-1]
            new_facts = steps[i].difference(prev_facts)
            if new_facts:
                md_content.append(f"\n**Step {i}:**")
                md_content.append(
                    f"- Previous facts: {', '.join(sorted(prev_facts))}")
                md_content.append(
                    f"- New facts derived: {', '.join(sorted(new_facts))}")

        return "\n".join(md_content)

    def generate_bc_diagram(self, goal, trace, kb_str):
        """Generate Markdown content for Backward Chaining trace with linear visualization"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        md_content = [
            "# Backward Chaining Visualization",
            f"\nGenerated: {timestamp}",
            "\n## Knowledge Base",
            f"```\nTELL\n{kb_str}\n\nASK\n{goal}\n```",
            "\n## Inference Process\n",
            "```mermaid",
            # Changed to RL for right-to-left linear flow (backward chaining)
            "graph RL"
        ]

        # Add goal node
        md_content.append(f"    Goal[Query<br/>{goal}]")

        # Add trace steps in a linear chain
        prev_node = "Goal"
        for i, (subgoal, status) in enumerate(reversed(list(enumerate(trace)))):
            node_id = f"N{i}"
            if status == "known":
                md_content.append(
                    f"    {node_id}[Found Fact<br/>{subgoal}] -->|Proves| {prev_node}")
            else:
                md_content.append(
                    f"    {node_id}[Need<br/>{subgoal}] -->|Requires| {prev_node}")
            prev_node = node_id

        md_content.append("```\n")

        # Add explanation
        md_content.append("### Reasoning Chain")
        for i, (subgoal, status) in enumerate(trace, 1):
            md_content.append(f"\n**Step {i}:**")
            if status == "known":
                md_content.append(f"- Found fact: {subgoal}")
            else:
                md_content.append(f"- Attempting to prove: {subgoal}")

        return "\n".join(md_content)

    def save_visualization(self, content, base_filename):
        """Save visualization content to a Markdown file with timestamp"""
        # Create 'visualizations' directory if it doesn't exist
        os.makedirs('visualizations', exist_ok=True)

        # Generate timestamp for unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{base_filename}_{timestamp}.md"

        # Save the content
        filepath = os.path.join('visualizations', filename)
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Visualization saved to: {filepath}")

    def forward_chaining(self, query, kb_str):
        """Forward chaining algorithm with visualization"""
        new_facts = set(self.facts)
        steps = [set(new_facts)]

        while True:
            added = set()
            for premise, conclusion in self.rules:
                premises = premise.split('&')
                if all(p.strip() in new_facts for p in premises) and conclusion not in new_facts:
                    added.add(conclusion)

            if not added:
                break

            new_facts.update(added)
            steps.append(set(new_facts))

        if self.visualize:
            fc_content = self.generate_fc_diagram(steps, kb_str, query)
            self.save_visualization(fc_content, 'forward_chaining')

        return query in new_facts, list(new_facts)

    def backward_chaining(self, query, kb_str):
        """Backward chaining algorithm with visualization"""
        trace = []

        def bc_aux(goal, visited):
            if goal in self.facts:
                trace.append((goal, "known"))
                return True

            if goal in visited:
                return False

            visited.add(goal)

            for premise, conclusion in self.rules:
                if conclusion == goal:
                    premises = premise.split('&')
                    trace.append(
                        (f"{' AND '.join(premises)} => {goal}", "rule"))

                    if all(bc_aux(p.strip(), visited.copy()) for p in premises):
                        return True

            return False

        result = bc_aux(query, set())

        if self.visualize:
            bc_content = self.generate_bc_diagram(query, trace, kb_str)
            self.save_visualization(bc_content, 'backward_chaining')

        return result, trace


def main():
    # Example usage
    kb_str = "p2=> p3; p3 => p1; c => e; b&e => f; f&g => h; p2&p1&p3 =>d; p1&p3 => c; a; b; p2;"
    query = "d"

    engine = InferenceEngine()
    engine.parse_kb(kb_str)

    # Run both algorithms with visualization
    fc_result, fc_facts = engine.forward_chaining(query, kb_str)
    bc_result, bc_trace = engine.backward_chaining(query, kb_str)

    # Print results
    print(f"\nForward Chaining Result: {'YES' if fc_result else 'NO'}")
    print(f"Backward Chaining Result: {'YES' if bc_result else 'NO'}")


if __name__ == "__main__":
    main()
