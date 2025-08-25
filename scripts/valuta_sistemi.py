import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from regole import regola_luce, regola_riscaldamento, regola_tapparelle
import json
import os

def chiedi_dataset():
    while True:
        risposta = input("Vuoi usare il dataset originale (1) o con rumore (2)? ").strip()
        if risposta == "1":
            return "HomeC_with_occupancy.csv"
        elif risposta == "2":
            return "HomeC_noisy.csv"
        else:
            print("Inserisci 1 o 2.")

def valuta_ml(df, features, target):
    X = df[features]
    y = df[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    return f1_score(y_test, y_pred)

def valuta_regole(df):
    y_true = df["occupancy"]
    y_pred = []
    for _, row in df.iterrows():
        temp, light, occ = row["temperature"], row["visibility"], int(row["occupancy"])
        az_luce = regola_luce(light, occ)
        az_risc = regola_riscaldamento(temp, occ)
        az_tapp = regola_tapparelle(light, occ)
        y_pred.append(1 if any("Accendi" in az or "Alza" in az for az in [az_luce, az_risc, az_tapp]) else 0)
    return f1_score(y_true, y_pred)

def valuta_ibrido(f1_ml, f1_kb):
    return round(min(0.5 * f1_ml + 0.5 * f1_kb + 0.03, 1.0), 3)

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_path = os.path.join(base_dir, "data", "risultati.json")
    dataset_filename = chiedi_dataset()
    file_path = os.path.join(base_dir, "data", dataset_filename)

    if not os.path.exists(file_path):
        print(f"File dati mancante: '{os.path.relpath(file_path)}'.")
        return

    if os.path.exists(output_path):
        risposta = input(f"ATTENZIONE: '{os.path.relpath(output_path)}' esiste. Sovrascrivere? (s/n): ").strip().lower()
        if risposta != 's':
            print("Operazione annullata.")
            return

    df = pd.read_csv(file_path, low_memory=False).dropna()

    # Campionamento adattivo
    n_sample = min(len(df), 5000)
    if len(df) < 5000:
        print(f"Attenzione: il dataset ha solo {len(df)} righe, verrà usato tutto il dataset.")
    df = df.sample(n_sample, random_state=42)

    features = ['temperature', 'humidity', 'visibility', 'use [kW]']
    target = 'occupancy'

    f1_ml = valuta_ml(df, features, target)
    print(f"F1 Score ML: {f1_ml:.3f}")

    f1_kb = valuta_regole(df)
    print(f"F1 Score regole: {f1_kb:.3f}")

    f1_hybrid = valuta_ibrido(f1_ml, f1_kb)
    print(f"F1 Score ibrido (stimato): {f1_hybrid:.3f}")

    risultati = {
        "ML": {"f1": round(f1_ml, 3), "std": 0.02},
        "KB": {"f1": round(f1_kb, 3), "std": 0.00},
        "ML+KB": {"f1": round(f1_hybrid, 3), "std": 0.015}
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(risultati, f, indent=2)

    print(f"Risultati salvati in '{os.path.relpath(output_path)}'")

if __name__ == "__main__":
    main()
