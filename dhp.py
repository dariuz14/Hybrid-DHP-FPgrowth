from collections import defaultdict
from itertools import combinations

class DHP:
    def __init__(self, min_support, dim_hash_table, transactions, large): 
        self.min_support = min_support
        self.dim_hash_table = dim_hash_table

        self.transactions = [set(t) for t in transactions]
        # Threshold to switch from hashing to non-hashing
        self.LARGE = large

    def _count_support(self, candidates, k):
        candidate_support = defaultdict(int) # Count support for each candidate itemset
        item_counts = defaultdict(int) # Count occurrences of individual items in candidates

        reduced_transactions = []

        for transaction in self.transactions:
            for candidate in candidates:
                if candidate.issubset(transaction):
                    candidate_support[candidate] += 1

                    for item in candidate:
                        item_counts[item] += 1

            transaction = [item for item, count in item_counts.items() if count >= k]
            if len(transaction) > k:
                reduced_transactions.append(set(transaction))
            item_counts.clear()
        
        self.transactions = reduced_transactions

        return candidate_support

    def _generate_candidates(self, prev_frequent, k, frequent_buckets=None, hashing=True):
        candidates = set()
        prev_list = list(prev_frequent)

        for i in range(len(prev_list)):
            for j in range(i+1, len(prev_list)):
                union = prev_list[i] | prev_list[j]

                if len(union) == k:
                    if hashing:
                        bucket = self._hash_function(tuple(union))
                        if bucket not in frequent_buckets:
                            continue

                        valid = True
                        for subset in combinations(union, k-1):
                            if frozenset(subset) not in prev_frequent:
                                valid = False
                                break
                        
                        if valid:
                            candidates.add(union)
                    else:
                        candidates.add(union)
            
        return candidates
        
    def _make_hash_table(self, frequent_k, k):
        hash_table = defaultdict(int)
        frequent_k_set = set(frequent_k)
        item_counts = defaultdict(int)

        reduced_transactions = []
        
        for transaction in self.transactions:
            # Transaction too small to form (k+1)-itemsets so it disregarded
            if len(transaction) <= k:
                continue
            # Genera tutti i possibili (k+1)-itemsets dalla transazione
            for itemset in combinations(transaction, k + 1):
                # Verifica che tutti i k-subset siano frequenti
                valid = True
                for subset in combinations(itemset, k):
                    if frozenset(subset) not in frequent_k_set:
                        valid = False
                        break
                
                if valid:
                    bucket = self._hash_function(itemset)
                    hash_table[bucket] += 1
                    for item in transaction:
                        item_counts[item] += 1

            reduced_transactions.append({item for item in transaction if item_counts[item] > 0})
            item_counts.clear()

        self.transactions = reduced_transactions
    
        return hash_table


    def _hash_function(self, itemset):
        hash_value = sum((i+1) * item for i, item in enumerate(sorted(itemset)))
        return hash_value % self.dim_hash_table
    
    def _build_hash_table(self, k):
        hash_table = defaultdict(int)

        for transaction in self.transactions:
            for itemset in combinations(transaction, k):
                bucket = self._hash_function(itemset)
                hash_table[bucket] += 1

        return hash_table
    
    def _get_frequent_buckets(self, hash_table):
        return {bucket for bucket, count in hash_table.items() if count >= self.min_support}

    def run(self):

        # Part 1: search for frequent 1-itemsets 
        item_counts = defaultdict(int) # Conto la frequenza di ogni singolo item
        for transaction in self.transactions:
            for item in transaction:
                item_counts[item] += 1
        
        frequent_1 = [frozenset([item]) for item, count in item_counts.items() if count >= self.min_support]

        print(f'Numero di frequent 1-itemset: {len(frequent_1)}')

        all_frequent = [(itemset, item_counts[list(itemset)[0]]) for itemset in frequent_1] # Lista di tuple (itemset, support)
        
        prev_frequent = frequent_1

        # Part 2: search for frequent k-itemsets, k >= 2
        k = 2

        # Construct hash table for k-itemsets
        hash_table = self._build_hash_table(k)
        frequent_buckets = self._get_frequent_buckets(hash_table)

        while len(frequent_buckets) >= self.LARGE:
            # Generate candidate k-itemsets, set di frozenset
            # Qui posso fare una modifica nel caso in cui non si usa piu l'hash table come nella parte 3
            candidates = self._generate_candidates(prev_frequent, k, frequent_buckets) 

            if not candidates:
                break

            candidate_support = self._count_support(candidates, k)

            # Frequent k-itemsets using candidate support
            frequent_k = [itemset for itemset, count in candidate_support.items() if count >= self.min_support] 

            if not frequent_k:
                break

            all_frequent.extend([(itemset, candidate_support[itemset]) for itemset in frequent_k])

            if not self.transactions:
                break

            hash_table = self._make_hash_table(frequent_k, k)

            frequent_buckets = self._get_frequent_buckets(hash_table)
            prev_frequent = frequent_k
            k += 1
        
        # Part 3: continue without hashing
        candidates = self._generate_candidates(prev_frequent, k, frequent_buckets)

        while candidates:
            candidate_support = self._count_support(candidates, k)
            self.transactions = [t for t in self.transactions if len(t) > k]

            frequent_k = [itemset for itemset, count in candidate_support.items() if count >= self.min_support]
            all_frequent.extend([(itemset, candidate_support[itemset]) for itemset in frequent_k])

            if not frequent_k or not self.transactions:
                break

            candidates = self._generate_candidates(frequent_k, k, hashing=False)
            k += 1

        return all_frequent


            



                        
            


        