# RISWIS Demo

Run this to see how RISWIS changes ranking before an LLM ever sees the data.

This demo shows, with real output, how trust policy can override semantic similarity — and makes that behavior visible.

---

## Get the Code

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

## Run It

```bash
# 1. Create environment
python -m venv testenv

# 2. Activate (Windows)
testenv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. IMPORTANT: Generate embeddings (required on first run)
python -m src.retrieval.doc_embeddings

# 5. Run the demo
python demo.py
```

---

## ⚠️ Common First-Run Issue

If you see an error like:

```
Missing embeddings file: data/doc_embeddings.npz
```

or

```
Doc 'doc_101' path does not exist
```

It means embeddings have not been generated yet.

Fix:

```bash
python -m src.retrieval.doc_embeddings
```

Then run:

```bash
python demo.py
```

---

## What You’ll See

Each result includes:

- raw_rank → semantic similarity only  
- weighted_rank → after trust weighting  
- delta → how far a document moved  

You can see exactly how ranking changed.

---

## Change the Outcome

```bash
python demo.py --t1 1.2
python demo.py --t1 1.3
python demo.py --t1 1.5
```

Higher values increase the influence of trusted sources.

---

## Change the Query

```bash
python demo.py --query "feeling drained every day"
python demo.py --query "why am I tired all the time"
```

Small wording changes affect semantic ranking — RISWIS shows how policy responds.

---

## What to Watch For

semantic winner ≠ policy winner  

When this happens, trust weighting has overridden similarity.

---

## What This Shows

- semantic similarity is not always the final decision  
- trust policy can change ranking order  
- ranking behavior is visible and repeatable  

---

## Next

This is the demo.  
The full system is in README.md.