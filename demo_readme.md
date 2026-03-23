# RISWIS Demo

Run this to see how RISWIS changes ranking before an LLM ever sees the data.

This demo shows, with real output, how trust policy can override semantic similarity — and makes that behavior visible.

---

## Run It

python -m venv testenv
testenv\Scripts\activate
pip install -r requirements.txt

python demo.py

---

## What You’ll See

Each result includes:

- raw_rank → semantic similarity only  
- weighted_rank → after trust weighting  
- delta → how far a document moved  

You can see exactly how ranking changed.

---

## Change the Outcome

python demo.py --t1 1.2  
python demo.py --t1 1.3  
python demo.py --t1 1.5  

Higher values increase the influence of trusted sources.

---

## Change the Query

python demo.py --query "feeling drained every day"  
python demo.py --query "why am I tired all the time"  

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