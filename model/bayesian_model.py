import scipy.special as sp
import numpy as np
import pandas as pd
import pymc as pm
import matplotlib.pyplot as plt
import arviz as az
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score, confusion_matrix, roc_curve, precision_recall_curve
from typing import List
import os
import json


class LogisticRegressionModel:
    def __init__(self, features: List[str], target: str, output_path='model/results'):
        self.features = features
        self.target = target
        self.output_path = output_path
        os.makedirs(self.output_path, exist_ok=True)
        self.model = None
        self.trace = None
        self.scaler = StandardScaler()
        self.posterior_mean = None

    def load_and_preprocess_data(self, file_path: str):
        data = pd.read_csv(file_path, low_memory=False)
        data = data.dropna(subset=self.features + [self.target])
        data = data[data[self.target].isin([0, 1])]
        return data

    def scale_features(self, X: pd.DataFrame) -> np.ndarray:
        return self.scaler.fit_transform(X)

    def build_bayesian_model(self, X_scaled: np.ndarray, y: np.ndarray):
        with pm.Model() as self.model:
            intercept = pm.Normal("intercept", mu=0, sigma=10)
            coefs = pm.Normal("coefs", mu=0, sigma=10, shape=len(self.features))
            logits = intercept + pm.math.dot(X_scaled, coefs)
            pm.Bernoulli("likelihood", logit_p=logits, observed=y)

    def sample_posterior_distribution(self, draws: int = 2000, tune: int = 1000, target_accept: float = 0.9, return_inferencedata: bool = True):
        if self.model is None:
            raise ValueError("Model not built yet. Call build_model first.")
        
        with self.model:  
            self.trace = pm.sample(draws, tune=tune, target_accept=target_accept, return_inferencedata=return_inferencedata)
            self.posterior_mean = self.trace.posterior.mean(dim=("chain", "draw"))
            az.plot_trace(logistic_model.trace)
            plt.savefig(os.path.join(self.output_path, 'trace_plot.png'))
            plt.close()

    def summarize_posterior(self, hdi_prob: float = 0.95):
        if self.trace is None:
            raise ValueError("Trace not found. Call sample first.")

        summary = az.summary(self.trace, hdi_prob=hdi_prob)
        summary_csv_path = os.path.join(self.output_path, 'posterior_summary.csv')
        summary.to_csv(summary_csv_path)

        summary_renamed = summary.copy()
        new_index = []
        for name in summary_renamed.index:
            if name.startswith("coefs["):
                idx = int(name.split("[")[1].strip("]"))
                new_index.append(self.features[idx])
            else:
                new_index.append(name)
        summary_renamed.index = new_index
        
        fig, ax = plt.subplots(figsize=(min(20, summary.shape[1] * 2), summary.shape[0] * 0.4 + 1))
        ax.axis('off')
        table = ax.table(
            cellText=summary_renamed.values,
            colLabels=summary_renamed.columns,
            rowLabels=summary_renamed.index,
            cellLoc='center',
            loc='center'
        )
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.5)
        summary_png_path = os.path.join(self.output_path, 'posterior_summary.png')
        plt.savefig(summary_png_path, bbox_inches='tight')
        plt.close()

    def plot_posterior_coefficients(self, hdi_prob: float = 0.95):
        if self.trace is None:
            raise ValueError("Trace not found. Call sample first.")
        if not hasattr(self, 'features'):
            raise ValueError("Feature names not found. Set self.features before calling this method.")

        fig, ax = plt.subplots(figsize=(8, len(self.features) * 0.5))
        az.plot_forest(
            self.trace,
            var_names=["coefs"],
            combined=True,
            hdi_prob=hdi_prob,
            ax=ax
        )

        ax.set_yticklabels(self.features)
        ax.set_title("Posterior Distributions of Coefficients")

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_path, 'posterior_coefficients.png'))
        plt.close(fig)

    def save_coefficients(self):
        if self.posterior_mean is None:
            raise ValueError("Posterior means not computed. Call sample first.")
        intercept_mean = self.posterior_mean["intercept"].values.item()
        coefs_mean = self.posterior_mean["coefs"].values.tolist()

        coefficients_data = {
            "intercept": intercept_mean,
            "coefficients": dict(zip(self.features, coefs_mean))
        }
        print("Intercept:", intercept_mean)
        print("Coefficients:")
        for feature, coef in zip(self.features, coefs_mean):
            print(f"  {str(feature):35s}: {coef:.8f}  ({'+' if coef > 0 else '-'})")

        filepath = os.path.join(self.output_path, 'model_coefficients.json')
        with open(filepath, 'w') as f:
            json.dump(coefficients_data, f, indent=4)
        print(f"Model coefficients saved to: {filepath}")

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if self.posterior_mean is None:
            raise ValueError("Posterior means not computed. Call sample first.")
        intercept_mean = self.posterior_mean["intercept"].values
        coefs_mean = self.posterior_mean["coefs"].values
        logits = intercept_mean + np.dot(X, coefs_mean)
        return sp.expit(logits)

    def predict(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        y_proba = self.predict_proba(X)
        return (y_proba >= threshold).astype(int)

    def evaluate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray, y_proba: np.ndarray = None):
        metrics = {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred),
            "recall": recall_score(y_true, y_pred),
            "confusion_matrix": confusion_matrix(y_true, y_pred).tolist()
        }
        if y_proba is not None:
            metrics["auc"] = roc_auc_score(y_true, y_proba)

        print("Evaluation Metrics:")
        for key, value in metrics.items():
            print(f"  {key}: {value}")

        filepath = os.path.join(self.output_path, 'evaluation_metrics.json')
        with open(filepath, 'w') as f:
            json.dump(metrics, f, indent=4)
        print(f"Evaluation metrics saved to: {filepath}")

    def plot_roc_curve(self, y_true: np.ndarray, y_proba: np.ndarray):
        fpr, tpr, _ = roc_curve(y_true, y_proba)
        auc_score = roc_auc_score(y_true, y_proba)
        plt.figure(figsize=(6, 5))
        plt.plot(fpr, tpr, label=f'AUC = {auc_score:.3f}')
        plt.plot([0, 1], [0, 1], 'k--', alpha=0.5)
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.title("ROC Curve")
        plt.legend()
        plt.grid()
        plt.savefig(os.path.join(self.output_path, 'roc_curve.png'))
        plt.close()

    def find_best_threshold(self, y_true: np.ndarray, y_proba: np.ndarray):
        precision, recall, thresholds = precision_recall_curve(y_true, y_proba)
        f1_scores = 2 * (precision * recall) / (precision + recall + 1e-9)
        best_idx = np.argmax(f1_scores)
        best_threshold = thresholds[best_idx]
        results = {
            "best_threshold": best_threshold.item(),
            "precision": precision[best_idx].item(),
            "recall": recall[best_idx].item(),
            "f1_score": f1_scores[best_idx].item()
        }
        print(f"Best threshold (by F1): {results['best_threshold']:.2f}")
        print(f"Precision: {results['precision']:.2f}")
        print(f"Recall: {results['recall']:.2f}")
        print(f"F1 Score: {results['f1_score']:.2f}")

        filepath = os.path.join(self.output_path, 'best_threshold.json')
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=4)
        print(f"Best threshold results saved to: {filepath}")
        return best_threshold, precision, recall, thresholds, f1_scores

    def plot_precision_recall_f1(self, thresholds: np.ndarray, precision: np.ndarray, recall: np.ndarray, f1_scores: np.ndarray, best_threshold: float):
        plt.figure(figsize=(8, 5))
        plt.plot(thresholds, precision[:-1], label='Precision')
        plt.plot(thresholds, recall[:-1], label='Recall')
        plt.plot(thresholds, f1_scores[:-1], label='F1 Score')
        plt.axvline(best_threshold, color='red', linestyle='--', label='Best Threshold')
        plt.xlabel('Threshold')
        plt.ylabel('Score')
        plt.title('Precision / Recall / F1 vs Threshold')
        plt.legend()
        plt.grid()
        plt.savefig(os.path.join(self.output_path, 'precision_recall_f1.png'))
        plt.close()


if __name__ == "__main__":
    target_column = 'is_default'
    feature_columns = ['credit_score', 'loan_age', 'original_combined_loan_to_value',
                       'original_debt_to_income_ratio', 'current_interest_rate']
    data_file_path = 'data/combined_dataset/data.csv'
    output_directory = 'model/results'

    logistic_model = LogisticRegressionModel(features=feature_columns, target=target_column, output_path=output_directory)

    # Load dataset
    data = logistic_model.load_and_preprocess_data(data_file_path)
    X = data[feature_columns]
    y = data[target_column].values

    # Scale features
    X_scaled = logistic_model.scale_features(X)

    # Build and sample the Bayesian Logistic Regression model
    logistic_model.build_bayesian_model(X_scaled, y)
    logistic_model.sample_posterior_distribution()

    # Summarize and plot the posterior
    logistic_model.summarize_posterior()
    logistic_model.plot_posterior_coefficients()
    logistic_model.save_coefficients()

    # Make predictions and evaluate
    y_proba = logistic_model.predict_proba(X_scaled)
    y_pred = logistic_model.predict(X_scaled)
    logistic_model.evaluate_metrics(y, y_pred, y_proba)
    logistic_model.plot_roc_curve(y, y_proba)

    # Find the best threshold and evaluate again
    best_threshold, precision, recall, thresholds, f1_scores = logistic_model.find_best_threshold(y, y_proba)
    y_pred_best_threshold = logistic_model.predict(X_scaled, threshold=best_threshold)
    logistic_model.evaluate_metrics(y, y_pred_best_threshold)
    logistic_model.plot_precision_recall_f1(thresholds, precision, recall, f1_scores, best_threshold)