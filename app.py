from flask import Flask, render_template, jsonify, request, url_for
import docker
import psutil
import time
import json
import os
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
import threading
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
update_lock = threading.Lock()

# Docker client configuration
def get_docker_client():
    try:
        # If docker host, use it, otherwise use the default
        if os.environ.get("DOCKER_HOST"):
            return docker.DockerClient(base_url=os.environ.get("DOCKER_HOST"))
        # Else throw error, do not let the app run
        else:
            raise Exception("DOCKER_HOST is not set")
    except Exception as e:
        print(f"Error creating Docker client: {str(e)}")
        return None

# Initialize database
def init_db():
    conn = sqlite3.connect("groups.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS group_names (
            original_name TEXT PRIMARY KEY,
            display_name TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_display_name(original_name):
    try:
        conn = sqlite3.connect("groups.db")
        c = conn.cursor()
        c.execute("SELECT display_name FROM group_names WHERE original_name = ?", (original_name,))
        result = c.fetchone()
        conn.close()
        # Si no hay resultado o el display_name es None, retornar el original
        if not result or not result[0]:
            return original_name
        return result[0]
    except Exception as e:
        print(f"Error getting display name: {str(e)}")
        return original_name

cached_stats = {
    "stats": {},
    "groups": {},
    "system_stats": {"cpu_percent": 0, "ram_percent": 0, "total_ram": 0}
}

def update_stats():
    if not update_lock.acquire(blocking=False):
        return
    
    try:
        client = get_docker_client()
        if not client:
            print("Failed to connect to Docker daemon")
            return

        containers = client.containers.list()
        stats = {}
        groups = {}
        
        # Calcular stats del sistema
        system_stats = {
            "cpu_percent": psutil.cpu_percent(interval=None),
            "ram_percent": psutil.virtual_memory().percent,
            "total_ram": round(psutil.virtual_memory().total / (1024.0 ** 3), 2),
            "docker_cpu_percent": 0,
            "docker_ram_percent": 0
        }
        
        total_docker_cpu = 0
        total_docker_ram = 0
        
        # Recolectar estadísticas
        for container in containers:
            try:
                name = container.name
                suffix = name.split("-")[-1]
                display_suffix = get_display_name(suffix)
                
                stats_dict = container.stats(stream=False)
                inspect = container.attrs
                
                cpu_limit = None
                if inspect["HostConfig"]["NanoCpus"] > 0:
                    cpu_limit = inspect["HostConfig"]["NanoCpus"] / 1e9
                
                memory_limit_mb = None
                if inspect["HostConfig"]["Memory"] > 0:
                    memory_limit_mb = round(inspect["HostConfig"]["Memory"] / (1024.0 * 1024.0), 2)
                
                cpu_delta = stats_dict["cpu_stats"]["cpu_usage"]["total_usage"] - stats_dict["precpu_stats"]["cpu_usage"]["total_usage"]
                system_delta = stats_dict["cpu_stats"]["system_cpu_usage"] - stats_dict["precpu_stats"]["system_cpu_usage"]
                cpu_percent = 0.0
                if system_delta > 0:
                    cpu_percent = (cpu_delta / system_delta) * 100.0
                
                memory_usage = stats_dict["memory_stats"].get("usage", 0)
                memory_limit = stats_dict["memory_stats"].get("limit", 1)
                memory_percent = (memory_usage / memory_limit) * 100.0
                
                container_stats = {
                    "cpu_percent": round(cpu_percent, 2),
                    "cpu_limit": cpu_limit,
                    "memory_percent": round(memory_percent, 2),
                    "memory_usage_mb": round(memory_usage / (1024.0 * 1024.0), 2),
                    "memory_limit_mb": memory_limit_mb
                }
                
                stats[name] = container_stats
                
                # Inicializamos el grupo si no existe
                if display_suffix not in groups:
                    groups[display_suffix] = {
                        "containers": [],
                        "total_cpu": 0,
                        "total_memory_mb": 0,  # Cambiado a MB directamente
                        "original_name": suffix
                    }
                
                groups[display_suffix]["containers"].append(name)
                groups[display_suffix]["total_cpu"] += cpu_percent
                groups[display_suffix]["total_memory_mb"] += container_stats["memory_usage_mb"]
                
                # Sumar al total de Docker
                total_docker_cpu += cpu_percent
                total_docker_ram += memory_usage
                
            except Exception as e:
                print(f"Error getting stats for {name}: {str(e)}")
                continue
        
        # Calcular porcentajes de Docker
        system_stats["docker_cpu_percent"] = round(total_docker_cpu, 2)
        system_stats["docker_ram_percent"] = round(
            (total_docker_ram / psutil.virtual_memory().total) * 100, 2
        )
        
        # Redondear los totales después de sumar todo
        for group in groups.values():
            group["total_cpu"] = round(group["total_cpu"], 2)
            group["total_memory_mb"] = round(group["total_memory_mb"], 2)
        
        global cached_stats
        cached_stats = {
            "stats": stats, 
            "groups": groups, 
            "system_stats": system_stats
        }
    except Exception as e:
        print(f"Error connecting to Docker: {str(e)}")
    finally:
        update_lock.release()

@app.route("/api/rename-group", methods=["POST"])
def rename_group():
    data = request.json
    conn = sqlite3.connect("groups.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO group_names (original_name, display_name) VALUES (?, ?)",
             (data["old_name"], data["new_name"]))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

executors = {
    "default": ThreadPoolExecutor(max_workers=1)
}
scheduler = BackgroundScheduler(executors=executors)
scheduler.add_job(func=update_stats, trigger="interval", seconds=15, max_instances=1, coalesce=True)
scheduler.start()

@app.route("/")
def index():
    return render_template("index.html", 
                         stats=cached_stats["stats"], 
                         groups=cached_stats["groups"], 
                         system_stats=cached_stats["system_stats"])

@app.route("/api/stats")
def get_stats():
    return jsonify(cached_stats)

if __name__ == "__main__":
    init_db()
    # Check Docker connection before starting
    if not get_docker_client():
        print("Cannot start application: Docker connection failed")
        exit(1)
    update_stats()  # Initial stats
    app.run(host="0.0.0.0", port=3000, debug=True) 