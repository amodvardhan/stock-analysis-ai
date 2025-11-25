"""
=============================================================================
Model Monitoring Service
=============================================================================
Performance tracking, drift detection, and retraining pipeline.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import structlog
import numpy as np

logger = structlog.get_logger()


class ModelMonitoringService:
    """Service for monitoring AI model performance and detecting drift."""
    
    @staticmethod
    def track_prediction_accuracy(
        predictions: List[Dict[str, Any]],
        actual_outcomes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Track prediction accuracy over time.
        
        Args:
            predictions: List of model predictions
            actual_outcomes: List of actual outcomes
        
        Returns:
            Accuracy metrics
        """
        try:
            if len(predictions) != len(actual_outcomes):
                return {"error": "Mismatched prediction and outcome counts"}
            
            correct = 0
            total = len(predictions)
            
            for pred, actual in zip(predictions, actual_outcomes):
                pred_action = pred.get("action", "hold")
                actual_action = actual.get("action", "hold")
                
                if pred_action == actual_action:
                    correct += 1
            
            accuracy = (correct / total * 100) if total > 0 else 0
            
            return {
                "accuracy": accuracy,
                "correct_predictions": correct,
                "total_predictions": total,
                "calculated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("accuracy_tracking_error", error=str(e))
            return {"error": str(e)}
    
    @staticmethod
    def detect_data_drift(
        current_data: Dict[str, Any],
        baseline_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Detect data drift in input features.
        
        Args:
            current_data: Current data distribution
            baseline_data: Baseline data distribution
        
        Returns:
            Drift detection results
        """
        try:
            drift_detected = False
            drift_features = []
            
            # Compare key features
            features_to_check = ["price", "volume", "volatility", "rsi", "pe_ratio"]
            
            for feature in features_to_check:
                current_val = current_data.get(feature, 0)
                baseline_val = baseline_data.get(feature, 0)
                
                if baseline_val == 0:
                    continue
                
                # Calculate percentage change
                change = abs((current_val - baseline_val) / baseline_val * 100)
                
                # Flag if change > 20%
                if change > 20:
                    drift_detected = True
                    drift_features.append({
                        "feature": feature,
                        "baseline": baseline_val,
                        "current": current_val,
                        "change_percentage": change
                    })
            
            return {
                "drift_detected": drift_detected,
                "drift_features": drift_features,
                "severity": "high" if len(drift_features) > 3 else "medium" if drift_detected else "low",
                "recommendation": "Retrain model" if drift_detected else "Model is stable",
                "detected_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("drift_detection_error", error=str(e))
            return {"error": str(e)}
    
    @staticmethod
    def calculate_model_performance(
        predictions: List[Dict[str, Any]],
        actuals: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive model performance metrics.
        
        Args:
            predictions: Model predictions
            actuals: Actual outcomes
        
        Returns:
            Performance metrics
        """
        try:
            # Calculate accuracy
            accuracy_metrics = ModelMonitoringService.track_prediction_accuracy(predictions, actuals)
            
            # Calculate precision, recall, F1 for each action
            actions = ["buy", "sell", "hold"]
            metrics_by_action = {}
            
            for action in actions:
                tp = sum(1 for p, a in zip(predictions, actuals) 
                        if p.get("action") == action and a.get("action") == action)
                fp = sum(1 for p, a in zip(predictions, actuals) 
                         if p.get("action") == action and a.get("action") != action)
                fn = sum(1 for p, a in zip(predictions, actuals) 
                        if p.get("action") != action and a.get("action") == action)
                
                precision = tp / (tp + fp) if (tp + fp) > 0 else 0
                recall = tp / (tp + fn) if (tp + fn) > 0 else 0
                f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                
                metrics_by_action[action] = {
                    "precision": precision,
                    "recall": recall,
                    "f1_score": f1,
                    "true_positives": tp,
                    "false_positives": fp,
                    "false_negatives": fn
                }
            
            # Calculate average confidence
            avg_confidence = np.mean([p.get("confidence", 0) for p in predictions]) if predictions else 0
            
            return {
                "overall_accuracy": accuracy_metrics.get("accuracy", 0),
                "metrics_by_action": metrics_by_action,
                "average_confidence": avg_confidence,
                "total_predictions": len(predictions),
                "calculated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("performance_calculation_error", error=str(e))
            return {"error": str(e)}
    
    @staticmethod
    def should_retrain(
        performance_metrics: Dict[str, Any],
        drift_results: Dict[str, Any],
        last_retrain_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Determine if model should be retrained.
        
        Args:
            performance_metrics: Current performance metrics
            drift_results: Data drift detection results
            last_retrain_date: Date of last retraining
        
        Returns:
            Retraining recommendation
        """
        try:
            should_retrain = False
            reasons = []
            
            # Check accuracy threshold
            accuracy = performance_metrics.get("overall_accuracy", 100)
            if accuracy < 60:
                should_retrain = True
                reasons.append(f"Low accuracy: {accuracy:.1f}%")
            
            # Check for data drift
            if drift_results.get("drift_detected"):
                should_retrain = True
                reasons.append("Data drift detected")
            
            # Check time since last retrain
            if last_retrain_date:
                days_since_retrain = (datetime.utcnow() - last_retrain_date).days
                if days_since_retrain > 30:
                    should_retrain = True
                    reasons.append(f"Last retrain was {days_since_retrain} days ago")
            
            return {
                "should_retrain": should_retrain,
                "reasons": reasons,
                "recommended_action": "Initiate retraining pipeline" if should_retrain else "Continue monitoring",
                "checked_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("retrain_decision_error", error=str(e))
            return {"error": str(e)}

