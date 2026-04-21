# 🚢 TCP Battleship

A multiplayer Battleship game implemented in Python using TCP sockets. Two players connect over a network and take turns trying to sink each other's fleet.

---

## 📌 Features

- Two-player gameplay over TCP
- Turn-based attack system
- Grid-based ship placement
- Hit/miss tracking
- Simple terminal or graphical interface (depending on your implementation)

---

## 🛠️ Technologies Used

- Python 3  
- `socket` (TCP networking)  
- Optional: `pygame` for GUI  

---

## 📂 Project Structure
tcp-battleship/
│
├── server.py # Handles connections and game coordination
├── client.py # Player client
├── game.py # Game logic (board, ships, rules)
├── utils.py # Helper functions
└── README.md

---

## 🚀 How to Run

### 1. Start the server
```bash
python server.py
```
If playing over a network, update the server IP in client.py:
```python
HOST = "your.server.ip"
PORT = 12345
```
🎮 How to Play
Each player places their ships on a grid
Players take turns entering coordinates (e.g., A5, B7)
The game reports:
Hit 💥
Miss 🌊
First player to sink all enemy ships wins
🌐 Networking Details
Protocol: TCP
Default Port: 12345
One server, two clients
Server manages:
Turn order
Game state
Communication between players
