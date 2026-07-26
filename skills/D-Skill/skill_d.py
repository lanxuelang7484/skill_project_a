import yaml
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
GLOBAL_CONFIG_PATH = BASE_DIR / "global_config.yaml"
CONTEXT_PATH = BASE_DIR / "runtime/context.json"

def load_global_config():
    with open(GLOBAL_CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def run_skill_d():
    global_cfg = load_global_config()
    project_id = global_cfg["project_id"]
    print(f"【D-Skill】开始生成报告，项目编号:{project_id}")

    with open(CONTEXT_PATH, "r", encoding="utf-8") as f:
        ctx = json.load(f)

    ctx["skill_d"] = {
        "final_report": f"项目{project_id}巡检报告：数据校验结果={ctx['skill_c']}",
        "project_status": "completed"
    }
    #ctx["final_report"] = f"项目{project_id}巡检报告：数据校验结果={ctx['check_result']}"
    #ctx["project_status"] = "completed"

    with open(CONTEXT_PATH, "w", encoding="utf-8") as f:
        json.dump(ctx, f, ensure_ascii=False, indent=2)

    print("✅ D-Skill 执行完成，整条流水线结束")
    return True

if __name__ == "__main__":
    run_skill_d()
