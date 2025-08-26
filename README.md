🏠 Smart Home Ibrido (ML + KB)

Progetto per il corso di Intelligenza Conoscitiva (ICon) – A.A. 2024/2025
Autore: Antonio Granato

📌 Descrizione del progetto

Il progetto implementa un sistema intelligente per automazione domestica (Smart Home), capace di suggerire azioni (es. accendere luci, climatizzatori, alzare tapparelle) sulla base di:

Condizioni ambientali: temperatura, luce, umidità, consumo energetico.

Presenza di persone (occupancy): stimata manualmente o tramite ML.

Sono stati sviluppati e confrontati tre approcci:

Knowledge-Based (KB): ragionamento simbolico tramite ontologia OWL e regole condizionali.

Machine Learning (ML): classificazione supervisionata (Random Forest, Logistic Regression, SVM).

Sistema Ibrido: integrazione tra ML e KB con diverse strategie di fusione.

🛠 Tecnologie utilizzate

Python 3.x

pandas – gestione e analisi dati

scikit-learn – Machine Learning

OWLready2 – modellazione e gestione dell’ontologia

matplotlib – grafici di analisi e valutazione

▶ Come eseguire il sistema

Il punto di ingresso principale è main.py.
Avvia il sistema con:

python main.py


Questo mostrerà un menu numerato con tutte le opzioni (analisi dati, creazione ontologia, addestramento ML, valutazione, ecc.).

⚠ Importante: Avvia il progetto sempre da main.py. I singoli script sono pensati solo per test o sviluppo.

✅ Requisiti

Python >= 3.8
