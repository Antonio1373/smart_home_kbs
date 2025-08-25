import os
import warnings
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import StratifiedKFold, cross_val_score
from joblib import dump
import numpy as np


MODELLI = {
    "1": ("RandomForest", RandomForestClassifier(n_estimators=150, random_state=42)),
    "2": ("LogisticRegression", LogisticRegression(max_iter=1000, n_jobs=None, solver='lbfgs')),
    "3": ("SVM", SVC(probability=True, kernel='rbf', C=1.0, gamma='scale', random_state=42)),
}


def chiedi_dataset():
    while True:
        risposta = input("Vuoi usare il dataset originale (1) o con rumore (2)? ").strip()
        if risposta == "1":
            return "HomeC_with_occupancy.csv"
        elif risposta == "2":
            return "HomeC_noisy.csv"
        else:
            print("Inserisci 1 o 2.")


def chiedi_modello():
    print("Scegli il modello da addestrare:")
    print("1) RandomForest  2) LogisticRegression  3) SVM")
    scelta = input("Selezione [1]: ").strip() or "1"
    return MODELLI.get(scelta, MODELLI["1"])  # (nome, istanza)


def carica_dati(file_path, sample_size=None, random_state=42):
    if not os.path.exists(file_path):
        print(f" File '{os.path.relpath(file_path, os.getcwd())}' mancante.")
        if "noisy" in os.path.basename(file_path).lower():
            print(" Assicurati di aver creato il dataset rumoroso (il punto 9.).")
        else:
            print(" Assicurati di aver eseguito 'il punto 1'.")
        return None

    print(f" File trovato: '{os.path.relpath(file_path, os.getcwd())}'")
    print(f" Caricamento dataset '{os.path.relpath(file_path)}'...")

    df = pd.read_csv(file_path, low_memory=False)
    df = df.dropna(subset=['temperature', 'humidity', 'visibility', 'use [kW]', 'occupancy'])

    if sample_size is not None:
        actual_sample_size = min(sample_size, len(df))
        df = df.sample(actual_sample_size, random_state=random_state)
        print(f" Campionamento : {len(df)} righe.")
    else:
        print(f" Dataset caricato: {len(df)} righe.")
    return df


def prepara_dati(df, features, target):
    X = df[features]
    y = df[target]
    return X, y


def valuta_cv(model, X, y, cv=5):
    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        f1 = cross_val_score(model, X, y, cv=skf, scoring='f1')
    return f1


def salva_modello(model, base_dir, model_name):
    model_path_generic = os.path.join(base_dir, "data", "modello.joblib")
    model_path_named = os.path.join(base_dir, "data", f"modello_{model_name.lower()}.joblib")
    os.makedirs(os.path.dirname(model_path_generic), exist_ok=True)
    dump(model, model_path_generic)
    dump(model, model_path_named)
    print(f" Modello salvato in: {os.path.relpath(model_path_generic)} e {os.path.relpath(model_path_named)}")


def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    dataset_filename = chiedi_dataset()
    (model_name, model_instance) = chiedi_modello()

    file_path = os.path.join(base_dir, "data", dataset_filename)
    df = carica_dati(file_path, sample_size=10000)
    if df is None:
        return

    features = ['temperature', 'humidity', 'visibility', 'use [kW]']
    target = 'occupancy'

    X, y = prepara_dati(df, features, target)

    if len(np.unique(y)) < 2:
        print(" ATTENZIONE: il target 'occupancy' ha una sola classe nel dataset.")
        return

    print(f"Valutazione {model_name} con 5-fold CV (F1 score)...")
    scores_f1 = valuta_cv(model_instance, X, y, cv=5)
    print(f" F1 mean: {scores_f1.mean():.4f}  std: {scores_f1.std():.4f}")

    print(" Addestramento modello finale su tutto il dataset...")
    model_instance.fit(X, y)

    salva_modello(model_instance, base_dir, model_name)

    if hasattr(model_instance, "feature_importances_"):
        importances = model_instance.feature_importances_
        print("\nImportanza delle feature:")
        for feat, imp in zip(features, importances):
            print(f" - {feat}: {imp:.4f}")

    print("\nOperazione completata.")


if __name__ == "__main__":
    main()