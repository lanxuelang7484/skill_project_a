import json
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
STATE_FILE = BASE_DIR / "runtime/execution_state.json"
LOG_FILE = BASE_DIR / "runtime/run.log"

# 固定执行顺序
SKILL_INFO = [
    {
        "name": "A-Skill",
        "script": BASE_DIR / "skills/A-Skill/skill_a.py"
    },
    {
        "name": "B-Skill",
        "script": BASE_DIR / "skills/B-Skill/skill_b.py"
    },
    {
        "name": "C-Skill",
        "script": BASE_DIR / "skills/C-Skill/skill_c.py"
    },
    {
        "name": "D-Skill",
        "script": BASE_DIR / "skills/D-Skill/skill_d.py"
    }
]

def init_runtime():
    runtime_dir = BASE_DIR / "runtime"
    runtime_dir.mkdir(exist_ok=True)
    if not STATE_FILE.exists():
        #初始化写入执行状态数据，字典默认为空
        json.dump({"finished": [], "last_skill": None}, open(STATE_FILE, "w", encoding="utf-8"), indent=2)

def load_state():
    return json.load(open(STATE_FILE, "r", encoding="utf-8"))

def save_state(state):
    json.dump(state, open(STATE_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

def write_log(msg):
    from datetime import datetime
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{t}] {msg}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)
    print(line.strip())

def can_run_skill(target_name):
    state = load_state()
    finished = state["finished"]
    # 生成器表达式获取对应skill信息的下标和技能组信息，返回i下标值
    idx = next(i for i, s in enumerate(SKILL_INFO) if s["name"] == target_name)
    # 校验前面所有skill是否全部完成
    for prev in SKILL_INFO[:idx]:
        if prev["name"] not in finished:
            return False, f"前置技能【{prev['name']}】未执行，不能运行{target_name}"
    return True, "允许执行"

def execute_skill(skill_name):
    ok, msg = can_run_skill(skill_name)
    if not ok:
        write_log(f"❌ {msg}")
        return False

    #生成器表达式获取对应skill信息
    skill_item = next(s for s in SKILL_INFO if s["name"] == skill_name)
    script_path = str(skill_item["script"])
    write_log(f"===== 启动 {skill_name} 脚本：{script_path} =====")

    # 调用独立skill脚本进程执行
    ret = subprocess.run([sys.executable, script_path])
    if ret.returncode != 0:
        write_log(f"❌ {skill_name} 执行异常，返回码：{ret.returncode}")
        return False

    # skill执行成功，更新state字典状态
    state = load_state()
    if skill_name not in state["finished"]:
        state["finished"].append(skill_name)
    state["last_skill"] = skill_name
    save_state(state)
    write_log(f"✅ {skill_name} 执行成功并已经记录状态")
    return True

def reset_all():
    import os
    runtime_dir = BASE_DIR / "runtime"
    for f in runtime_dir.glob("*"):
        os.unlink(f)
    init_runtime()
    write_log("🔄 全部运行状态已重置，可以从头执行流水线")

def run_full_pipeline():
    for skill in SKILL_INFO:
        if not execute_skill(skill["name"]):
            write_log("流水线中断！")
            return
    write_log("🎉 完整流水线 A→B→C→D 全部执行完毕！")

if __name__ == "__main__":
    init_runtime()
    print("==== Skill统一调度器 ====")
    print("1. 一键完整流水线 A→B→C→D")
    print("2. 单独执行A-Skill")
    print("3. 单独执行B-Skill")
    print("4. 单独执行C-Skill")
    print("5. 单独执行D-Skill")
    print("9. 重置所有运行状态")
    opt = input("输入选项：")
    if opt == "1":
        run_full_pipeline()
    elif opt == "2":
        execute_skill("A-Skill")
    elif opt == "3":
        execute_skill("B-Skill")
    elif opt == "4":
        execute_skill("C-Skill")
    elif opt == "5":
        execute_skill("D-Skill")
    elif opt == "9":
        reset_all()
    else:
        print("无效选项")
