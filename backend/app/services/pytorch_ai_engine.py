"""
PyTorch Neural AI Engine for AksharAI Literacy Platform.

Includes deep neural network architectures for:
1. AksharAIProficiencyNet - Multi-Skill Proficiency Classifier & Score Predictor
2. AksharAIHandwritingNet - 4-Metric Visual & Structural Handwriting Evaluator
3. AksharAIPronunciationNet - Phoneme & Acoustic Speech Pronunciation Quality Estimator
4. AksharAIRecommendationNet - Neural Collaborative & Adaptive Lesson Recommender
"""

import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Any, Tuple, Optional


class AksharAIProficiencyNet(nn.Module):
    """
    PyTorch Deep Multilayer Perceptron for Learner Proficiency Level Classification.
    Inputs: [reading_score, word_formation_score, grammar_score, literature_score, speech_confidence, handwriting_accuracy, milestone_pct]
    Outputs: [zero_prob, foundational_prob, functional_prob, proficient_prob] + predicted_score
    """
    def __init__(self, input_dim: int = 7, hidden_dim: int = 64, num_classes: int = 4):
        super(AksharAIProficiencyNet, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.bn1 = nn.BatchNorm1d(hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.bn2 = nn.BatchNorm1d(hidden_dim // 2)
        self.dropout = nn.Dropout(0.2)
        
        # Classification Head (Proficiency Level Probabilities)
        self.classifier = nn.Linear(hidden_dim // 2, num_classes)
        
        # Regression Head (Composite Proficiency Score 0-100)
        self.regressor = nn.Linear(hidden_dim // 2, 1)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        # Handle 1D single-instance input by unsqueezing batch dimension
        is_single = (x.dim() == 1)
        if is_single:
            x = x.unsqueeze(0)

        h = F.relu(self.fc1(x))
        if x.size(0) > 1:
            h = self.bn1(h)
        h = F.relu(self.fc2(h))
        if x.size(0) > 1:
            h = self.bn2(h)
        h = self.dropout(h)

        logits = self.classifier(h)
        probs = F.softmax(logits, dim=-1)
        
        # Regressed score constrained to 0 - 100 via Sigmoid scaling
        score = torch.sigmoid(self.regressor(h)) * 100.0

        if is_single:
            probs = probs.squeeze(0)
            score = score.squeeze(0)

        return probs, score


class AksharAIHandwritingNet(nn.Module):
    """
    PyTorch Deep Evaluator for Handwriting Stroke Quality & Guideline Discipline.
    Inputs: [line_discipline, cluster_separation, width_coverage, stray_stroke_ratio, pixel_density, target_count_diff]
    Outputs: predicted_stroke_accuracy (0 - 100)
    """
    def __init__(self, input_dim: int = 6, hidden_dim: int = 32):
        super(AksharAIHandwritingNet, self).__init__()
        self.layer1 = nn.Linear(input_dim, hidden_dim)
        self.layer2 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.output = nn.Linear(hidden_dim // 2, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        is_single = (x.dim() == 1)
        if is_single:
            x = x.unsqueeze(0)

        h = F.leaky_relu(self.layer1(x), 0.1)
        h = F.leaky_relu(self.layer2(h), 0.1)
        # Scale output score between 0 and 100
        score = torch.sigmoid(self.output(h)) * 100.0

        if is_single:
            score = score.squeeze(0)

        return score


class AksharAIPronunciationNet(nn.Module):
    """
    PyTorch Deep Acoustic & Phoneme Speech Evaluator.
    Inputs: [phoneme_match_ratio, pitch_contour_std, energy_db, pause_ratio, tempo_wpm]
    Outputs: predicted_speech_accuracy (0 - 100) & fluency_index (0 - 100)
    """
    def __init__(self, input_dim: int = 5, hidden_dim: int = 32):
        super(AksharAIPronunciationNet, self).__init__()
        self.shared = nn.Linear(input_dim, hidden_dim)
        self.accuracy_head = nn.Linear(hidden_dim, 1)
        self.fluency_head = nn.Linear(hidden_dim, 1)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        is_single = (x.dim() == 1)
        if is_single:
            x = x.unsqueeze(0)

        h = F.relu(self.shared(x))
        accuracy = torch.sigmoid(self.accuracy_head(h)) * 100.0
        fluency = torch.sigmoid(self.fluency_head(h)) * 100.0

        if is_single:
            accuracy = accuracy.squeeze(0)
            fluency = fluency.squeeze(0)

        return accuracy, fluency


class AksharAIRecommendationNet(nn.Module):
    """
    PyTorch Deep Neural Collaborative & Content Recommender.
    Computes affinity score between Learner Feature Embedding & Module Candidate Embedding.
    """
    def __init__(self, learner_feature_dim: int = 8, module_feature_dim: int = 8, embed_dim: int = 16):
        super(AksharAIRecommendationNet, self).__init__()
        self.learner_fc = nn.Linear(learner_feature_dim, embed_dim)
        self.module_fc = nn.Linear(module_feature_dim, embed_dim)
        
        self.combined_fc1 = nn.Linear(embed_dim * 2, 32)
        self.combined_fc2 = nn.Linear(32, 1)

    def forward(self, learner_feats: torch.Tensor, module_feats: torch.Tensor) -> torch.Tensor:
        l_emb = F.relu(self.learner_fc(learner_feats))
        m_emb = F.relu(self.module_fc(module_feats))

        cat = torch.cat([l_emb, m_emb], dim=-1)
        h = F.relu(self.combined_fc1(cat))
        affinity = torch.sigmoid(self.combined_fc2(h)) * 100.0
        return affinity


class PyTorchAIEngine:
    """
    Unified Inference & Training Service managing PyTorch Deep Learning Models.
    """
    LEVEL_NAMES = ["ZERO", "FOUNDATIONAL", "FUNCTIONAL", "PROFICIENT"]

    def __init__(self, model_dir: Optional[str] = None):
        self.model_dir = model_dir or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models"))
        os.makedirs(self.model_dir, exist_ok=True)

        # Initialize PyTorch Models
        self.proficiency_net = AksharAIProficiencyNet()
        self.handwriting_net = AksharAIHandwritingNet()
        self.pronunciation_net = AksharAIPronunciationNet()
        self.recommendation_net = AksharAIRecommendationNet()

        # Set evaluation mode by default
        self.proficiency_net.eval()
        self.handwriting_net.eval()
        self.pronunciation_net.eval()
        self.recommendation_net.eval()

    def predict_learner_proficiency(self, features: List[float]) -> Dict[str, Any]:
        """
        Runs PyTorch Neural Inference for learner proficiency classification & scoring.
        :param features: [reading, word_formation, grammar, literature, speech_conf, hw_acc, milestone_pct]
        :return: Dict containing predicted_level, probabilities, and predicted_score
        """
        with torch.no_grad():
            x = torch.tensor(features, dtype=torch.float32)
            probs, score = self.proficiency_net(x)
            
            probs_list = probs.numpy().tolist()
            pred_idx = int(torch.argmax(probs).item())
            
            return {
                "predicted_level": self.LEVEL_NAMES[pred_idx],
                "level_probabilities": {
                    self.LEVEL_NAMES[i]: round(probs_list[i], 4) for i in range(len(self.LEVEL_NAMES))
                },
                "predicted_composite_score": round(float(score.item()), 2)
            }

    def evaluate_handwriting_strokes(self, stroke_metrics: List[float]) -> Dict[str, Any]:
        """
        Runs PyTorch Neural Inference for handwriting stroke quality evaluation.
        :param stroke_metrics: [line_discipline, cluster_separation, width_coverage, stray_ratio, pixel_density, target_count_diff]
        """
        with torch.no_grad():
            x = torch.tensor(stroke_metrics, dtype=torch.float32)
            score = self.handwriting_net(x)
            val = float(score.item())
            return {
                "predicted_stroke_accuracy": round(val, 2),
                "quality_tier": "EXCELLENT" if val >= 80 else ("GOOD" if val >= 60 else "NEEDS_PRACTICE")
            }

    def evaluate_pronunciation_audio(self, acoustic_feats: List[float]) -> Dict[str, Any]:
        """
        Runs PyTorch Neural Inference for audio speech & phoneme accuracy evaluation.
        :param acoustic_feats: [phoneme_match_ratio, pitch_std, energy_db, pause_ratio, tempo_wpm]
        """
        with torch.no_grad():
            x = torch.tensor(acoustic_feats, dtype=torch.float32)
            acc, flu = self.pronunciation_net(x)
            return {
                "predicted_speech_accuracy": round(float(acc.item()), 2),
                "predicted_fluency_index": round(float(flu.item()), 2)
            }

    def score_module_recommendation(self, learner_feats: List[float], module_feats: List[float]) -> float:
        """
        Runs PyTorch Deep Recommender scoring for a candidate module.
        """
        with torch.no_grad():
            lf = torch.tensor(learner_feats, dtype=torch.float32).unsqueeze(0)
            mf = torch.tensor(module_feats, dtype=torch.float32).unsqueeze(0)
            affinity = self.recommendation_net(lf, mf)
            return round(float(affinity.squeeze().item()), 2)

    def train_proficiency_model(self, X_data: List[List[float]], Y_labels: List[int], epochs: int = 10, lr: float = 0.01) -> float:
        """
        Trains PyTorch ProficiencyNet using Adam optimizer & CrossEntropyLoss.
        """
        self.proficiency_net.train()
        optimizer = torch.optim.Adam(self.proficiency_net.parameters(), lr=lr)
        criterion = nn.CrossEntropyLoss()

        inputs = torch.tensor(X_data, dtype=torch.float32)
        targets = torch.tensor(Y_labels, dtype=torch.long)

        final_loss = 0.0
        for epoch in range(epochs):
            optimizer.zero_grad()
            probs, _ = self.proficiency_net(inputs)
            loss = criterion(probs, targets)
            loss.backward()
            optimizer.step()
            final_loss = float(loss.item())

        self.proficiency_net.eval()
        return final_loss

    def save_checkpoint(self, filename: str = "aksharai_pytorch_models.pt") -> str:
        """
        Saves all PyTorch model weights to file.
        """
        path = os.path.join(self.model_dir, filename)
        torch.save({
            "proficiency_net": self.proficiency_net.state_dict(),
            "handwriting_net": self.handwriting_net.state_dict(),
            "pronunciation_net": self.pronunciation_net.state_dict(),
            "recommendation_net": self.recommendation_net.state_dict()
        }, path)
        return path

    def load_checkpoint(self, filename: str = "aksharai_pytorch_models.pt") -> bool:
        """
        Loads PyTorch model state dict from saved checkpoint file.
        """
        path = os.path.join(self.model_dir, filename)
        if not os.path.exists(path):
            return False
        
        checkpoint = torch.load(path, weights_only=True)
        self.proficiency_net.load_state_dict(checkpoint["proficiency_net"])
        self.handwriting_net.load_state_dict(checkpoint["handwriting_net"])
        self.pronunciation_net.load_state_dict(checkpoint["pronunciation_net"])
        self.recommendation_net.load_state_dict(checkpoint["recommendation_net"])

        self.proficiency_net.eval()
        self.handwriting_net.eval()
        self.pronunciation_net.eval()
        self.recommendation_net.eval()
        return True
