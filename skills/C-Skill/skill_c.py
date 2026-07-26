import yaml
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
GLOBAL_CONFIG_PATH = BASE_DIR / "global_config.yaml"
CONTEXT_PATH = BASE_DIR / "runtime/context.json"

def load_global_config():
    with open(GLOBAL_CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def run_skill_c():
    global_cfg = load_global_config()
    mem_limit = global_cfg["memory_threshold"]
    disk_limit = global_cfg["disk_threshold"]
    print(f"【C-Skill】加载阈值配置，内存上限:{mem_limit},磁盘上限:{disk_limit}")

    with open(CONTEXT_PATH, "r", encoding="utf-8") as f:
        ctx = json.load(f)

    metrics = ctx["skill_b"]
    # 使用全局配置阈值校验
    check_result = metrics["memory_used"] < mem_limit and metrics["disk_usage"] < disk_limit
    ctx["skill_c"] = {
        "valid_metrics": metrics,
        "check_result": check_result,
    }
    #ctx["skill_c"] = metrics
    #ctx["check_result"] = check_result

    with open(CONTEXT_PATH, "w", encoding="utf-8") as f:
        json.dump(ctx, f, ensure_ascii=False, indent=2)

    print("✅ C-Skill 执行完成")
    return True

if __name__ == "__main__":
    run_skill_c()
