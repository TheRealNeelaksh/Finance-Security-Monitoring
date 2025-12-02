# Modern Financial Security System - Support Layer

This repository implements the "Support Layer" of a modern fraud detection system, focusing on collaboration, privacy, and transparency.

## 🏗️ System Architecture

The system is composed of three core enabling frameworks:

### 1. Generative AI (GANs) - Data Generation
*   **Goal:** Generate realistic, synthetic fraud data to train models against emerging threats without exposing real user PII.
*   **Tech:** `CTGAN` (Conditional Tabular GAN).
*   **Code:** `data_generation/train_gan.py`
*   **Output:** `phase1/synthetic_logins.csv`

### 2. Federated Learning (FL) - Collaborative Training
*   **Goal:** Enable multiple banks (simulated clients) to train a shared fraud detection model without sharing raw transaction logs.
*   **Tech:** `Flower` (flwr), `TensorFlow`.
*   **Code:** `phase1/fl_simulation.py`
*   **Output:** `phase1/model_autoencoder_federated.h5`

### 3. Explainable AI (XAI) - Transparency & Auditing
*   **Goal:** Provide human-readable explanations for why a transaction was flagged as high risk.
*   **Tech:** `SHAP` (SHapley Additive exPlanations).
*   **Code:** `phase2/explainability.py`
*   **Output:** `phase2/shap_explanation_force_plot.png`

---

## 🚀 How to Run

### Prerequisites
Install the required dependencies:
```bash
pip install ctgan flwr shap tensorflow pandas numpy scikit-learn geopy matplotlib ipython ray
```

### Option 1: Run the Full Pipeline (Recommended)
Open `full_pipeline_demo.ipynb` in Jupyter Notebook to run the end-to-end workflow interactively.

### Option 2: Run Individual Components

**Step 1: Generate Synthetic Data**
Train the GAN on seed data to create new synthetic logs.
```bash
python data_generation/train_gan.py
```

**Step 2: Train Distributed Model**
Simulate 3 banks training the Autoencoder collaboratively.
```bash
python phase1/fl_simulation.py
```

**Step 3: Explain Predictions**
Analyze a specific fraud instance using SHAP.
```bash
python phase2/explainability.py
```

---

## 📂 File Structure

*   `data_generation/`
    *   `datagen.py`: Original procedural generator (Seed data).
    *   `train_gan.py`: **[NEW]** GAN training script.
*   `phase1/`
    *   `feature_engine.py`: **[NEW]** Shared preprocessing logic.
    *   `models.py`: **[NEW]** Shared model definitions.
    *   `fl_simulation.py`: **[NEW]** Federated Learning simulation.
    *   `user_logins.csv`: Seed data.
    *   `synthetic_logins.csv`: GAN output.
*   `phase2/`
    *   `explainability.py`: **[NEW]** XAI script.
    *   `shap_explanation_force_plot.png`: Visualization output.
*   `full_pipeline_demo.ipynb`: **[NEW]** Integration notebook.

## 🧠 Integration Logic

1.  **GANs** ensure we have infinite data to train on, solving the "cold start" problem for new fraud patterns.
2.  **Federated Learning** ensures that this training can happen across borders and institutions without privacy violations.
3.  **XAI** ensures that when the system flags a user, an analyst can trust *why* (e.g., "Velocity > 800km/h"), reducing false positives and operational costs.
