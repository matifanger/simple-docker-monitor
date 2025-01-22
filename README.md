# 🐳 Docker Monitor

A sleek, real-time Docker container monitoring dashboard built with Python and modern web technologies.

![Docker Monitor Dashboard](https://i.imgur.com/QKJfHhm.png)

## ✨ Features

- Real-time monitoring of Docker containers
- System-wide Docker resource usage
- Container grouping by compose project
- Auto-refresh every 15 seconds
- Clean, modern UI with dark mode
- Mobile responsive design
- Change the name of container group

## 🚀 Quick Start

1. Clone the repository:
```bash
git clone https://github.com/matifanger/simple-docker-monitor.git
cd simple-docker-monitor
```

2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```

5. Run the application:
```bash
python app.py
```

6. Open your browser and navigate to `http://localhost:3000`

## 🔧 Configuration

The following environment variables can be configured in `.env`:

- `DOCKER_HOST` - Docker daemon socket (default: unix:///var/run/docker.sock)
- `DEVELOPMENT` - Enable development mode (default: false)

## 🚀 Deploy Using Docker 

1. Make sure Docker is installed on your system.  
   [Download Docker](https://www.docker.com/products/docker-desktop)

2. Clone the repository and navigate to the project directory:
   ```bash
   git clone https://github.com/matifanger/simple-docker-monitor.git
   cd simple-docker-monitor

3. Build the Docker image:
```
docker build -t simple-docker-monitor .
```

4. Run the Docker container:
```
docker run -d -p 3000:3000 -v /var/run/docker.sock:/var/run/docker.sock simple-docker-monitor
```

## 🛠️ Tech Stack

- Backend: Python, Flask
- Frontend: TailwindCSS, JavaScript
- Container Management: Docker SDK for Python

# 🎯 Improvement Checklist

## High Priority
- [ ] Add authentication system
- [ ] Connect via SSH
- [ ] Implement container logs viewing
- [ ] Add container start/stop/restart controls
- [ ] Implement error handling for Docker connection issues
- [ ] Add container health check status

## Medium Priority
- [ ] Add historical data tracking
- [ ] Implement container resource usage graphs
- [ ] Add container configuration viewing
- [ ] Implement search and filtering
- [ ] Add container network statistics

## Low Priority
- [ ] Add light/dark theme toggle
- [ ] Implement custom refresh intervals
- [ ] Add container environment variables viewing
- [ ] Implement container creation from UI
- [ ] Add export functionality for container stats

## Technical Debt
- [ ] Add comprehensive test coverage
- [ ] Implement proper logging system
- [ ] Add API documentation
- [ ] Optimize Docker stats collection
- [ ] Implement proper error boundaries

## Bugs
- [ ] When changing the name of the container, it is not immediate upon refresh

## 📝 License

MIT License - feel free to use this project however you'd like!

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.