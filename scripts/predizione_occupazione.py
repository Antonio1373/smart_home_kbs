import os
import warnings
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import StratifiedKFold, cross_val_score
from joblib import dump

# ---------------- CONFIGURAZIONE MODELLI ----------------
MODELLI = {
    "RandomForest": RandomForestClassifier(n_estimators=150, random_state=42),
    "LogisticRegression": LogisticRegression(max_iter=1000, solver='lbfgs'),
    "SVM": SVC(probability=True, kernel='rbf', C=1.0, gamma='scale', random_state=42),
}

# ---------------- FUNZIONI UTILI ----------------
def carica_dataset(percorso):
    if not os.path.exists(percorso):
        print(f"ERRORE: file dataset '{percorso}' non trovato.")
        return None
    df = pd.read_csv(percorso)
    print(f"Dataset caricato: {len(df)} righe.")
    return df

def prepara_dati(df, features, target):
    X = df[features]
    y = df[target]
    return X, y

def valuta_modello_cv(model, X, y, cv=5):
    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        scores = cross_val_score(model, X, y, cv=skf, scoring='f1')
    return scores

def salva_modello(model, base_dir, nome_modello):
    os.makedirs(os.path.join(base_dir, "data"), exist_ok=True)
    percorso_generico = os.path.join(base_dir, "data", "modello.joblib")
    percorso_specifico = os.path.join(base_dir, "data", f"modello_{nome_modello}.joblib")
    dump(model, percorso_generico)
    dump(model, percorso_specifico)
    print(f"Modello salvato in:\n - {os.path.relpath(percorso_generico)}\n - {os.path.relpath(percorso_specifico)}")

# ---------------- MAIN ----------------
def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    dataset_file = os.path.join(base_dir, "data", "SmartHome.csv")

    df = carica_dataset(dataset_file)
    if df is None:
        return

    # Selezione feature e target
    features = [
        'temperatura', 'umidita', 'illuminazione',
        'consumo_luce_kW', 'consumo_riscaldamento_kW',
        'consumo_climatizzatore_kW', 'consumo_tapparella_kW'
    ]
    target = 'occupazione'

    X, y = prepara_dati(df, features, target)

    if len(np.unique(y)) < 2:
        print("ERRORE: il target 'occupazione' ha una sola classe.")
        return

    # Tabella comparativa
    risultati = []

    print("\nValutazione di tutti i modelli con 5-fold CV (F1 score):")
    for nome_modello, modello in MODELLI.items():
        print(f"\n▶ {nome_modello} ...")
        scores = valuta_modello_cv(modello, X, y)
        f1_mean = scores.mean()
        f1_std = scores.std()
        print(f" F1 mean: {f1_mean:.4f}, std: {f1_std:.4f}")

        # Addestramento finale su tutto il dataset
        modello.fit(X, y)
        salva_modello(modello, base_dir, nome_modello)

        risultati.append({
            "Modello": nome_modello,
            "F1_mean": f1_mean,
            "F1_std": f1_std
        })

        # Feature importances per RandomForest
        if hasattr(modello, "feature_importances_"):
            print("Importanza delle feature:")
            for f, imp in zip(features, modello.feature_importances_):
                print(f" - {f}: {imp:.4f}")

    # Stampa tabella comparativa finale
    df_risultati = pd.DataFrame(risultati)
    print("\n=== Tabella comparativa modelli ===")
    print(df_risultati.to_string(index=False))

if __name__ == "__main__":
    main()
