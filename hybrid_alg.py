from dhp import DHP
from fpgrowth import FPgrowth
import time

class HybridAlg:
    def __init__(self, min_support, dim_dhp_hash_table, transactions, large, max_k):
        self.min_support = min_support
        self.min_size_per_fpg = max_k + 1     
        self.initial_dhp = DHP(min_support=min_support, dim_hash_table=dim_dhp_hash_table, transactions=transactions, large=large, max_k=max_k)

    def run(self):
        start_dhp = time.time()
        frequent_max_k_itemsets = self.initial_dhp.run()
        end_dhp = time.time()
        print(f"DHP execution time: {end_dhp - start_dhp:.4f} seconds")

        transactions_after_dhp = self.initial_dhp.get_transactions()
        
        frequent_itemsets_from_fpg = []
        if transactions_after_dhp is not None:
            print(f"Number of transactions after DHP:", len(transactions_after_dhp))
            fpg = FPgrowth(min_support=self.min_support, transactions=transactions_after_dhp, min_size=self.min_size_per_fpg)
            frequent_itemsets_from_fpg = fpg.run()
            print(f"From fpg: {frequent_itemsets_from_fpg}")
        
        return frequent_max_k_itemsets + frequent_itemsets_from_fpg
        
