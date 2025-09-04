import os
import warnings
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import StratifiedKFold, cross_val_score
from joblib import dump
import numpy as np

# ---------------- MODELLI DISPONIBILI ----------------
MODELLI = {
    "1": ("RandomForest", RandomForestClassifier(n_estimators=150, random_state=42)),
    "2": ("LogisticRegression", LogisticRegression(max_iter=1000, solver='lbfgs')),
    "3": ("SVM", SVC(probability=True, kernel='rbf', C=1.0, gamma='scale', random_state=42)),
}

def chiedi_modello():
    print("Scegli il modello da addestrare:")
    print("1) RandomForest  2) LogisticRegression  3) SVM")
    scelta = input("Selezione [1]: ").strip() or "1"
    return MODELLI.get(scelta, MODELLI["1"])

def carica_dati(file_path):
    if not os.path.exists(file_path):
        print(f"File '{os.path.relpath(file_path)}' non trovato.")
        return None
    df = pd.read_csv(file_path)
    print(f"✅ Dataset caricato: {len(df)} righe")
    return df

def prepara_dati(df, features, target):
    X = df[features]
    y = df[target]
    return X, y

def valuta_cv(model, X, y, cv=5):
    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        scores = cross_val_score(model, X, y, cv=skf, scoring='f1')
    return scores

def salva_modello(model, base_dir, model_name):
    os.makedirs(os.path.join(base_dir, "data"), exist_ok=True)
    path_generic = os.path.join(base_dir, "data", "modello.joblib")
    path_named = os.path.join(base_dir, "data", f"modello_{model_name}.joblib")
    dump(model, path_generic)
    dump(model, path_named)
    print(f"✅ Modello salvato in: {os.path.relpath(path_generic)} e {os.path.relpath(path_named)}")

# ---------------- MAIN ----------------
def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    dataset_file = os.path.join(base_dir, "data", "SmartHome.csv")
    model_name, model_instance = chiedi_modello()

    df = carica_dati(dataset_file)
    if df is None:
        return

    # Usiamo solo i dati grezzi dal CSV
    features = [
        'temperatura', 'umidita', 'illuminazione',
        'consumo_luce_kW', 'consumo_riscaldamento_kW',
        'consumo_climatizzatore_kW', 'consumo_tapparella_kW'
    ]
    target = 'occupazione'

    X, y = prepara_dati(df, features, target)

    if len(np.unique(y)) < 2:
        print("⚠ Il target 'occupazione' ha una sola classe nel dataset.")
        return

    print(f"\n🔹 Valutazione {model_name} con 5-fold CV (F1 score)...")
    scores = valuta_cv(model_instance, X, y)
    print(f" F1 mean: {scores.mean():.4f}  std: {scores.std():.4f}")

    print("\n🔹 Addestramento modello finale su tutto il dataset...")
    model_instance.fit(X, y)
    salva_modello(model_instance, base_dir, model_name)

    if hasattr(model_instance, "feature_importances_"):
        print("\nImportanza delle feature:")
        for f, imp in zip(features, model_instance.feature_importances_):
            print(f" - {f}: {imp:.4f}")

    print("\n✅ Operazione completata.")

if __name__ == "__main__":
    main()
