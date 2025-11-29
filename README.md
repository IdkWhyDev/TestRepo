# Final Project: 

## Stack:
1. Runtime: Python 3.10.
2. LLM model: gemini-2.5-flash.
3. Backend: FastAPI.
4. Interface: Streamlit.

## Prerequisites:
1. Gemini API key from: https://aistudio.google.com/

## Setup:
1. `git clone https://github.com/RifqiAnshariR/smart-split-bill.git`
2. `cd smart-split-bill`
3. `py -3.10 -m venv .venv` and activate it `.venv\Scripts\activate`
4. `pip install -r requirements.txt`
5. Make .env file contains: GOOGLE_API_KEY.

## How to run:
1. To run app: watchmedo auto-restart --patterns="*.*" -- .venv\Scripts\python.exe app.py
2. To export app: pyinstaller --noconfirm --onedir --windowed --name AppV1 --add-data "assets/model.onnx;assets" --add-data "assets/logs.txt;assets" app.py
3. To run Streamlit: streamlit run Home.py

## Evaluation:
Evaluation done on: 
- A
- B
- C

Results:
- A
- B

- C

## Release
[![Download](https://img.shields.io/github/v/release/IdkWhyDev/TestRepo?label=Download&style=for-the-badge)](https://github.com/IdkWhyDev/TestRepo/releases/latest)
