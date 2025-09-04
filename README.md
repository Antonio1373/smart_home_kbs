🏠 Smart Home Ibrido (ML + KB)

Progetto per il corso di Intelligenza Conoscitiva (ICon) – A.A. 2024/2025

Autore: Antonio Granato

📌 Obiettivo del progetto

Il progetto realizza un sistema Smart Home in grado di:

Suggerire azioni automatiche su dispositivi domestici (luci, riscaldamento, climatizzatore, tapparelle).

Considerare stato ambientale (temperatura, luce, umidità, consumo) e occupancy.

Integrare due approcci:

KB (Knowledge-Based): ontologia OWL + reasoning Pellet + regole Python.

ML (Machine Learning): RandomForest, LogisticRegression e SVM per predizione occupazione.

Produrre un sistema ibrido che combina inferenze della KB con predizioni ML.

🔑 Funzionalità principali
Script	Funzione

ontologia.py	Definizione della KB: classi, proprietà, sottoclassi derivate per il reasoning.

genera_istanze.py	Popolamento della KB con case, stanze, dispositivi, persone e stati ambientali.

regole.py	Regole Python per decidere azioni automatiche sui dispositivi.

genera_dataset.py	Generazione di dataset CSV dalla KB per addestramento ML.

applica_regole.py	Applicazione delle regole Python per creare istanze Azione nella KB.

predizione_occupazione.py	Addestramento e valutazione modelli ML per predire la presenza di persone.

analisi_KBS.py	Analisi delle stanze inferite dal reasoner e aggregazione delle azioni suggerite.

main.py	Menu principale per eseguire tutti gli script in sequenza.

🛠 Tecnologie utilizzate

Python 3.x

pandas – gestione dataset

scikit-learn – modelli ML

OWLready2 – gestione ontologia e reasoner Pellet

joblib – salvataggio dei modelli ML

uuid, random, os – generazione di dati e gestione filesystem

▶ Come eseguire il sistema

Il punto di ingresso principale è main.py.
Clonare il repository in locale con il seguente comando:

    git clone https://github.com/Antonio1373/smart_home_kbs.git 
    
Spostarsi nella root del progetto e avviare il sistema con il comando:

    python main.py


Questo mostrerà un menu numerato con tutte le opzioni.

Seguire le opzioni numerate per:

1) Creare ontologia

2) Generare istanze

3) Creare dataset

4) Applicare regole

5) Addestrare ML

6) Analizzare KB

⚠ Importante: Avvia il progetto sempre da main.py. I singoli script sono pensati solo per test o sviluppo.

✅ Requisiti

Python >= 3.8
