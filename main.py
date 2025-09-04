import subprocess
import os

MENU = {
    "1": ("Crea ontologia ambiente", "ontologia.py"),
    "2": ("Genera istanze smart home", "genera_istanze.py"),
    "3": ("Genera dataset", "genera_dataset.py"),
    "4": ("Applicazione delle regole SmartHome", "applica_regole.py"),
    "5": ("Predizione occupazione", "predizione_occupazione.py"),
    "6": ("Analisi KBS SmartHome", "analisi_KBS.py"),
}

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "scripts")

FILES_DA_ELIMINARE = [
    "data/SmartHome.csv",
    "data/report_KBS_reasoning.csv",
    "ontology/smarthome.owl",
    "ontology/smarthome_popolata.owl",
    "ontology/smarthome_con_azioni.owl",
    "data/modello_RandomForest.joblib",
    "data/modello_LogisticRegression.joblib",
    "data/modello_SVM.joblib",
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

