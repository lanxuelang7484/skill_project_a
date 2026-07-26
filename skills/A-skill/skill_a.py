import yaml
import json
import time
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
GLOBAL_CONFIG_PATH = BASE_DIR / "global_config.yaml"
CONTEXT_PATH = BASE_DIR / "runtime/context.json"

def load_global_config():
    with open(GLOBAL_CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def run_skill_a():
    # 1. 加载全局公共配置
    global_cfg = load_global_config()
    print(f"【A-Skill】加载全局配置，项目ID:{global_cfg['project_id']}, 服务器:{global_cfg['server_env']}")

    # 2. 初始化运行上下文
    ctx = {}
    ctx["global_config"] = global_cfg
    ctx["skill_a"] = {
        "os": global_cfg["server_env"],
        "python_version": "3.10+",
        "init_timestamp": time.time(),
        "init_finished": True
    }
    #ctx["skill_a"] = time.time()
    #ctx["init_finished"] = True

    # 持久化上下文供后续skill读取
    with open(CONTEXT_PATH, "w", encoding="utf-8") as f:
        json.dump(ctx, f, ensure_ascii=False, indent=2)

    print("✅ A-Skill 执行完成")
    return True

if __name__ == "__main__":
    run_skill_a()
