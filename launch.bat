@echo off
echo Installing required packages...
pip install -r requirements.txt

echo Starting ConnectX...
python main.py
pause 