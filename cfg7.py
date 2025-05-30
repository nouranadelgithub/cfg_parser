from graphviz import Digraph

class CFGParser:
    def __init__(self):
        self.grammar = {}
        self.start_symbol = ''
        self.node_count = 0
        self.memo = {}

    def add_rule(self, rule):
        head, body = rule.split('->')
        head = head.strip()
        # handle epsilon explicitly
        bodies = [b.strip().split() if b.strip() != 'epsilon' else [] for b in body.strip().split('|')]
        if not self.start_symbol:
            self.start_symbol = head
        if head in self.grammar:
            self.grammar[head].extend(bodies)
        else:
            self.grammar[head] = bodies

    def parse_input(self, input_string):
        tokens = input_string.strip().split()
        print(f"Tokens: {tokens}")
        self.memo = {}  # clear memo before parsing
        success, tree, final_pos = self._parse(self.start_symbol, tokens, 0)
        if success and final_pos == len(tokens):
            print("Valid string!")
            self._draw_tree(tree)
        else:
            print("Invalid string!")

    def _parse(self, symbol, tokens, position):
        # Memoization key
        key = (symbol, position)
        if key in self.memo:
            return self.memo[key]

        # Terminal symbol
        if symbol not in self.grammar:
            if position < len(tokens) and tokens[position] == symbol:
                self.memo[key] = (True, (symbol, []), position + 1)
                return self.memo[key]
            else:
                self.memo[key] = (False, None, position)
                return self.memo[key]

        # Non-terminal: try each production
        best_success = False
        best_tree = None
        best_pos = position

        for production in self.grammar[symbol]:
            if not production:  # epsilon production
                # Return a node with explicit epsilon child
                tree = (symbol, [("epsilon", [])])
                if position >= best_pos:
                    best_success = True
                    best_tree = tree
                    best_pos = position
                continue

            children = []
            current_pos = position
            matched = True
            for sym in production:
                success, subtree, next_pos = self._parse(sym, tokens, current_pos)
                if not success:
                    matched = False
                    break
                children.append(subtree)
                current_pos = next_pos
            if matched and current_pos >= best_pos:
                best_success = True
                best_tree = (symbol, children)
                best_pos = current_pos

        self.memo[key] = (best_success, best_tree, best_pos)
        return self.memo[key]

    def _draw_tree(self, tree):
        dot = Digraph()
        self.node_count = 0  # reset node count for fresh drawing
        self._add_nodes(dot, tree)
        dot.render('parse_tree', view=True, format='png')
        print("Parse tree saved as 'parse_tree.png'")

    def _add_nodes(self, dot, tree, parent=None):
        symbol, children = tree
        self.node_count += 1
        node_id = f'node{self.node_count}'
        dot.node(node_id, symbol)
        if parent:
            dot.edge(parent, node_id)
        for child in children:
            self._add_nodes(dot, child, node_id)

# ----------------------------

# Usage example:

parser = CFGParser()
print("Enter your grammar rules (e.g., S -> A B | epsilon). Type 'done' when finished:")
while True:
    rule = input()
    if rule.lower() == 'done':
        break
    parser.add_rule(rule)

input_string = input("Enter a string to parse (tokens separated by space): ")
parser.parse_input(input_string)
