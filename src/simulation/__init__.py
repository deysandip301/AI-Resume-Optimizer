"""Simulation module for recruiter behavior and ATS analysis."""
from src.simulation.gaze import generate_saliency_heatmap
from src.simulation.ats_check import scan_for_hidden_text

__all__ = ["generate_saliency_heatmap", "scan_for_hidden_text"]
