# RISWIS Demo Instructions

This demo shows how the Governance Retrieval Layer (GRL) changes ranking  
before results reach the LLM.

**Goal:**  
See how trust weighting (T1 / T2 / T3) affects which documents win.

---

## 0. Get the Code

You can either download or clone the repository.

### Option A — Download ZIP (easiest)

- Click the green **Code** button on GitHub  
- Select **Download ZIP**  
- Extract the folder  
- Open a terminal inside the extracted folder  

### Option B — Clone with Git

```bash
git clone https://github.com/ebysslabscodes/riswis.git
cd riswis
```

Make sure you are inside the `riswis` folder before continuing.

---

## 1. Setup (fresh environment recommended)

```bash
python -m venv testenv
testenv\Scripts\activate   # Windows

pip install -r requirements.txt
```

---

## 2. IMPORTANT: Generate embeddings (first run only)

```bash
python -m src.retrieval.doc_embeddings
```

This step is required before running the demo.  
It builds the document embeddings used for retrieval.

If you skip this step, you may see errors like:

- Missing embeddings file  
- Doc path does not exist  

---

## 3. Run the demo (default behavior)

```bash
python demo.py
```

This uses default multipliers:

- T1 = 1.5  
- T2 = 1.0  
- T3 = 0.7  

You will see:

- GRL Results (raw vs weighted ranking)  
- What changed (which documents moved)  
- Detection (whether a rank flip occurred)  

---

## 4. Change trust weighting (interactive demo)

```bash
python demo.py --t1 1.2
python demo.py --t1 1.3
python demo.py --t1 1.5
```

**What to observe:**

At **T1 = 1.2**
- Semantic winner stays on top  
- No rank flip  

At **T1 = 1.3**
- Higher trust documents take over  
- Rank flip occurs  

---

## 5. Change the query

```bash
python demo.py --query "why am I tired all the time"
```

Different queries may:

- show strong trust promotion  
- or show no rank flip at all  

---

## 6. What “Rank Flip” means

A rank flip happens when:

- The semantic winner (highest similarity)  
  is **NOT** the final winner  

- The policy-weighted result becomes the winner instead  

You will see:

⚠️ Rank flip detected: semantic winner and policy winner differ  

This means:  
GRL changed the outcome based on trust weighting.

---

## 7. Important Notes

- This demo temporarily overrides tier multipliers  
  but restores settings after each run  

- Core RISWIS logic is **NOT modified**  

- This is a demonstration of behavior,  
  not a full application or UI  

---

## 8. What this demo proves

- Ranking is not fixed — it is controllable  
- Trust policy can override similarity  
- All ranking decisions are visible and auditable  
- The system is reproducible across environments  

---

## End

This is the demo.  
The full system is in `README.md`.