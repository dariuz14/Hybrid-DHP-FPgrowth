from itertools import combinations
import random


def generate_transactions(num_transactions, num_items, avg_transaction_length, std_transaction_length, popular_items_ratio, 
                          popular_items_frequency, min_transaction_length=1, max_transaction_length=None):
    
    if max_transaction_length is None:
          max_transaction_length = num_items

    dataset = []

    num_popular = int(num_items*popular_items_ratio)
    popular_items = set(random.sample(range(1, num_items + 1), num_popular))

    for _ in range(num_transactions):
        length = int(random.gauss(avg_transaction_length, std_transaction_length))
        length = max(min_transaction_length, min(max_transaction_length, length))

        transaction = set()

        for item in popular_items:
            if random.random() < popular_items_frequency and len(transaction) < length:
                transaction.add(item)
        
        remaining_slot = length - len(transaction)
        if remaining_slot > 0:
            available_items = list(set(range(1, num_items + 1)) - transaction)
            additional_items = random.sample(available_items, min(remaining_slot, len(available_items)))
            transaction.update(additional_items)

        dataset.append(transaction)
    
    return dataset


def extract_association_rules(frequent_itemsets, min_confidence=0.6):
    freq_dict = {itemset: count for itemset, count in frequent_itemsets}

    rules = []

    for itemset, supp_itemset in freq_dict.items():
        k = len(itemset)
        if k < 2:
            continue  

        # Generate all possibile splits X -> Y from the itemset
        for i in range(1, k):
            for antecedent in combinations(itemset, i):
                antecedent = frozenset(antecedent)
                consequent = itemset - antecedent

                supp_antecedent = freq_dict.get(antecedent)
                
                # Calculate rule confidence
                confidence = supp_itemset / supp_antecedent

                # Save rule if confidence is greater or equal to min_confidence
                if confidence >= min_confidence:
                    rules.append({
                        "antecedent": antecedent,
                        "consequent": consequent,
                        "support": supp_itemset,
                        "confidence": confidence
                    })

    return rules