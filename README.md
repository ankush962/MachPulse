# MachPulse

Smartphone-powered predictive maintenance using vibration, sound and machine learning.

## What is MachPulse?

MachPulse turns a normal smartphone into a machine-health monitor.

The phone's accelerometer and microphone capture machine behaviour. The system processes the signals, detects unusual behaviour using machine learning, estimates machine health, and provides maintenance guidance.

## Basic Architecture

Android Phone
↓
Accelerometer + Microphone
↓
WebSocket
↓
FastAPI
↓
Signal Processing
↓
Machine Learning
↓
Machine Health
↓
React Dashboard
↓
Ollama
↓
Maintenance Advice

## Project Structure

- `android/` - Android sensor application
- `backend/` - FastAPI backend
- `ml/` - signal processing and machine learning
- `frontend/` - monitoring dashboard
- `data/` - local data and models
- `docs/` - documentation
- `tests/` - tests
- `scripts/` - utility scripts

## Main Features

### MVP

- Smartphone accelerometer monitoring
- Microphone-based machine sound monitoring
- Real-time sensor streaming
- Signal processing
- Machine-specific healthy baseline
- ML anomaly detection
- Machine health score
- Risk level
- Live monitoring dashboard
- AI maintenance guidance

### Future

- Fault classification
- Maintenance history
- Repair verification
- Edge AI
- Push notifications
- Multi-machine monitoring

## Technology

- Android + Kotlin
- Python
- FastAPI
- NumPy
- SciPy
- scikit-learn
- React
- Tailwind CSS
- SQLite
- Ollama
- GitHub

## Cost

MachPulse is designed as a zero-cost hackathon project.

The core system does not depend on paid APIs.

AI assistance uses a local Ollama model.

## Team

- Teammate 1 — Android + Sensors
- Teammate 2 — ML + Signal Processing
- Teammate 3 — Backend + Frontend + AI
