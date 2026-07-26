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

def run_skill_b():
    global_cfg = load_global_config()
    print(f"【B-Skill】全局配置加载完成，磁盘阈值：{global_cfg['disk_threshold']}")

    # 读取上一个skill上下文
    with open(CONTEXT_PATH, "r", encoding="utf-8") as f:
        ctx = json.load(f)

    # 本skill独有业务
    ctx["skill_b"] = {
        "memory_used": 42,
        "disk_usage": 56,
        "collect_finish_time": time.time()
    }
    #ctx["collect_finish_time"] = time.time()

    with open(CONTEXT_PATH, "w", encoding="utf-8") as f:
        json.dump(ctx, f, ensure_ascii=False, indent=2)

    print("✅ B-Skill 执行完成")
    return True

if __name__ == "__main__":
    run_skill_b()
