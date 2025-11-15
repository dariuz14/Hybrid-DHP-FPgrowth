from collections import defaultdict
from itertools import combinations

class FPNode:
    def __init__(self, item, count, parent):
        self.item = item
        self.count = count
        self.parent = parent
        self.children = []
        self.node_link = None
    
    def count_increment(self):
        self.count += 1

    def add_child(self, child_node):
        self.children.append(child_node)

class FPTree:
    def __init__(self):
        self.root = FPNode(None, 0, None)
        # Header table to link same items
        self.header_table = defaultdict(list)
    
    def insert_transaction(self, transaction, count=1):
        current_node = self.root

        for item in transaction:
            found_child = None

            for child in current_node.children:
                if child.item == item:
                    found_child = child
        
            if found_child:
                found_child.count_increment()
                current_node = found_child
            else:
                new_node = FPNode(item, count, current_node)
                current_node.add_child(new_node)
                current_node = new_node

                # Update header table
                if not self.header_table[item]:
                    self.header_table[item].append(new_node)
                else:
                    last_node = self.header_table[item][-1]
                    last_node.node_link = new_node
                    self.header_table[item].append(new_node)
    
    # Given a node, return all prefixes that lead to it 
    def get_path(self, node):
        path = []
        current_node = node
        count = current_node.count

        while current_node.parent is not None:
            current_node = current_node.parent
            if current_node != self.root:
                path.append(current_node.item)
            
        path.reverse()
        return (path, count)

    def _is_single_path(self):
        node = self.root
        while node.children:
            if len(node.children) > 1:
                return False
            node = node.children[0]
        return True
               
class FPgrowth:
    def __init__(self, min_support, transactions):
        self.min_support = min_support
        self.transactions = [list(t) for t in transactions]

        self.fp_tree = None
    
    def _get_all_items_in_path(self, tree):
        items = []
        node = tree.root
        while node.children:
            child = node.children[0]
            items.append((child.item, child.count))
            node = child
        return items
    
    def _generate_combinations(self, items, suffix):
        patterns = []
    
        # Generate all combinations of length 1 to len(items)
        for r in range(1, len(items) + 1):
            for combination in combinations(items, r):
                item_list = [item for item, count in combination]
                min_count = min(count for item, count in combination)
                
                # Add suffix
                pattern = item_list + suffix
                patterns.append((frozenset(pattern), min_count))
        
        return patterns

    def _mine_tree(self, tree, suffix=[]):
        patterns = []

        if tree._is_single_path():
            items = self._get_all_items_in_path(tree)
            if items:
                patterns.extend(self._generate_combinations(items, suffix))
            
            return patterns
        
        items_by_count = sorted(tree.header_table.items(),
                                key=lambda x: sum(node.count for node in x[1]))
        
        for item, nodes in items_by_count:
            support = sum(node.count for node in nodes)

            new_suffix = [item] + suffix
            patterns.append((frozenset(new_suffix), support))

            conditional_pb = []
            for node in nodes:
                path, count = tree.get_path(node)
                if path:
                    conditional_pb.append((path, count))
            
            # Build Conditional Pattern Base
            if conditional_pb:
                item_counts = defaultdict(int)
                for path, count in conditional_pb:
                    for i in path:
                        item_counts[i] += count
                
                frequent_items = {i for i, c in item_counts.items() if c >= self.min_support}

                if frequent_items:
                    filtered_paths = []
                    for path, count in conditional_pb:
                        new_path = [i for i in path if i in frequent_items]
                        if new_path:
                            new_path = sorted(new_path, key=lambda x: item_counts[x], reverse=True)
                            filtered_paths.append((new_path, count))

                    # Given the CPB, construct the conditional FP-tree
                    conditional_tree = FPTree()
                    for path, count in filtered_paths:
                        conditional_tree.insert_transaction(path, count)

                    # Recursive mining of patterns from the conditional FP-tree
                    patterns.extend(self._mine_tree(conditional_tree, new_suffix))

        return patterns    

    def run(self):
        item_counts = defaultdict(int)

        # Count items
        for transaction in self.transactions:
            for item in transaction:
                item_counts[item] += 1
        
        self.transactions = [sorted([item for item in t if item_counts[item] >= self.min_support], 
                                    key= lambda x: item_counts[x], 
                                    reverse=True) 
                                    for t in self.transactions
                                    ]
        
        # Build FP-Tree
        self.fp_tree = FPTree()
        for t in self.transactions:
            if t:
                self.fp_tree.insert_transaction(t)
        
        self.frequent_patterns = self._mine_tree(self.fp_tree)
        
        return self.frequent_patterns