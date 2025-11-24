# Hybrid-DHP-FPgrowth
Questa repository contiene il codice relativo all'algoritmo ibrido implementato che combina i vantaggi di DHP (Direct Hash and Pruning) e
FP-Growth (Frequent Pattern Growth) per la ricerca degli itemset frequenti e successiva estrazione di association-rules.

**Step 1:** *DHP*
- Generazione degli itemset candidati ad ogni iterazione utilizzando hashing (solo nella prima fase).
- Riduzione progressiva della dimensione del dataset.

**Step 2:** *FP-Growth* 
- Costruzione dell'FP-Tree sulla base del dataset ridotto.
- Estrazione dei pattern direttamente dall'albero.

**Step 3:** *Estrazione association-rules*