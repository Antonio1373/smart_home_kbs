import subprocess
import os

MENU = {
    "1": ("Analizza dati sensori", "analisi_dati.py"),
    "2": ("Crea ontologia ambiente", "ontologia.py"),
    "3": ("Genera istanze smart home", "genera_istanze.py"),
    "4": ("Predizione occupazione", "predizione_occupazione.py"),
    "5": ("Avvia sistema ibrido", "sistema_ibrido.py"),
    "6": ("Valuta prestazioni sistemi", "valuta_sistemi.py"),
    "7": ("Applica regole a CSV", "applica_regole_a_csv.py"),
    "8": ("Valutazione risultati", "valutazione.py"),
    "9": ("Crea dataset rumoroso", "dataRumoroso.py"),
}

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "scripts")

FILES_DA_ELIMINARE = [
    "data/HomeC_with_occupancy.csv",
    "ontology/smarthome.owl",
    "ontology/smarthome_popolata.owl",
    "ontology/smarthome_updated.owl",
    "ontology/smarthome_rules_applied.owl",
    "data/risultati.json",
    "results/valutazione.png",
    "data/HomeC_noisy.csv",
    "data/modello_randomforest.joblib",
    "data/modello_logisticregression.joblib",
    "data/modello_svm.joblib",
    "data/modello.joblib"
]

print(" Pulizia iniziale dei file generati...")
for file in FILES_DA_ELIMINARE:
    path = os.path.abspath(file)                
    if os.path.exists(path):                       
        os.remove(path)                           
        print(f" RIMOSSO: {file}")
print(" PULIZIA COMPLETATA.\n")


while True:
    print("\n--- Sistema Smart Home ---")
    for k, (descrizione, _) in MENU.items():
        print(f"{k}. {descrizione}")
    print("0. Esci")

    scelta = input("Seleziona un'opzione (es. 1): ").strip()

    if scelta == "0":
        print("Uscita dal programma.")
        break

    elif scelta in MENU:
        descrizione, script_file = MENU[scelta]
        script_path = os.path.join(SCRIPTS_DIR, script_file)
        if os.path.exists(script_path):                                            
            print(f"\n▶ Esecuzione: {descrizione}...\n")
            subprocess.run(["python", script_path])
        else:
            print(f" Errore: il file '{script_path}' non esiste.")             
    else:
        print(" Scelta non valida. Riprova.")                                   

