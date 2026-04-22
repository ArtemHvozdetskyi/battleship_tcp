# 🚢 TCP Battleship

A multiplayer Battleship game implemented in Python using TCP sockets. Two players connect over a network and take turns trying to sink each other's fleet.

---

## 📌 Features

- Two-player gameplay over TCP
- Turn-based attack system
- Grid-based ship placement
- Hit/miss tracking
- Simple graphical interface 

---

## 🛠️ Technologies Used

- Python 3  
- `socket` (TCP networking)  
- `pygame` for GUI  

---

## 📂 Project Structure
```
.
├── button.py
├── game.py
├── server_client.py
├── server.py
├── text_input.py
└── textures
    ├── button.png


```
## Instaling dependencies
```bash
pip install requirements.txt
```

## 🚀 How to Run

### 1. Start the server
```bash
python server.py
```
### 2. Start client

```bash
python game.py
```
# 🎮 How to Play
Each player places their ships on a grid <br>
Players take turns entering coordinates (e.g., A5, B7) <br>
The game reports: <br>
Hit 💥 <br>
Miss 🌊 <br>
First player to sink all enemy ships wins
## 🌐 Networking Details
Protocol: TCP <br>
Server IP: You  chose IPv6<br>
Default Port: 51005 <br>
One server, two clients
## Server manages:
Game state<br>
Communication between players
# 🐛 Issues

If you find a bug, please open an issue describing the problem.

# 📄 License

This project is licensed under the MIT License.

# 🙋‍♂️ Author

Artem Hvozdetskyi <br>
GitHub: 