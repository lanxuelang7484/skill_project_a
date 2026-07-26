import json
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path


class SkillScheduler:
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir if base_dir else Path(__file__).parent
        self.runtime_dir = self.base_dir / "runtime"
        self.state_file = self.runtime_dir / "execution_state.json"
        self.log_file = self.runtime_dir / "run.log"

        self.skill_info = [
            {"name": "A-Skill", "script": self.base_dir / "skills/A-Skill/skill_a.py"},
            {"name": "B-Skill", "script": self.base_dir / "skills/B-Skill/skill_b.py"},
            {"name": "C-Skill", "script": self.base_dir / "skills/C-Skill/skill_c.py"},
            {"name": "D-Skill", "script": self.base_dir / "skills/D-Skill/skill_d.py"}
        ]

    def init_runtime(self):
        self.runtime_dir.mkdir(exist_ok=True)
        if not self.state_file.exists():
            # 新增skipped字段存储被主动跳过的技能
            init_state = {"finished": [], "skipped": [], "last_skill": None}
            self._save_state(init_state)

    def _load_state(self):
        with open(self.state_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_state(self, state):
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def write_log(self, msg: str):
        t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{t}] {msg}\n"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(line)
        print(line.strip())

    def can_run_skill(self, target_name: str) -> tuple[bool, str]:
        """
        【核心改动】支持跳过逻辑
        前置技能两种情况视为满足条件：
        1. 正常执行完成 finished
        2. 被主动设置跳过 skipped
        """
        state = self._load_state()
        finished = state["finished"]
        skipped = state["skipped"]

        target_idx = -1
        for idx, skill in enumerate(self.skill_info):
            if skill["name"] == target_name:
                target_idx = idx
                break
        if target_idx == -1:
            return False, f"不存在技能：{target_name}"

        pre_skills = self.skill_info[:target_idx]
        for pre in pre_skills:
            pre_name = pre["name"]
            if pre_name not in finished and pre_name not in skipped:
                return False, f"前置技能【{pre_name}】未执行且未设置跳过，不能运行{target_name}"
        return True, "允许执行"

    def skip_skill(self, skill_name: str) -> bool:
        """主动标记跳过某个技能，等效执行完成"""
        ok, msg = self.can_run_skill(skill_name)
        if not ok:
            self.write_log(f"❌ 无法跳过{skill_name}: {msg}")
            return False

        state = self._load_state()
        if skill_name not in state["skipped"]:
            state["skipped"].append(skill_name)
        state["last_skill"] = skill_name
        self._save_state(state)
        self.write_log(f"⏭️ 成功标记跳过技能：{skill_name}")
        return True

    def execute_skill(self, skill_name: str) -> bool:
        ok, msg = self.can_run_skill(skill_name)
        if not ok:
            self.write_log(f"❌ {msg}")
            return False

        # 判断是否已经被标记跳过
        state = self._load_state()
        if skill_name in state["skipped"]:
            self.write_log(f"ℹ️ {skill_name} 已标记跳过，不再执行脚本")
            return True

        skill_item = next(s for s in self.skill_info if s["name"] == skill_name)
        script_path = str(skill_item["script"])
        self.write_log(f"===== 启动 {skill_name} 脚本：{script_path} =====")

        ret = subprocess.run([sys.executable, script_path])
        if ret.returncode != 0:
            self.write_log(f"❌ {skill_name} 执行异常，返回码：{ret.returncode}")
            return False

        state = self._load_state()
        if skill_name not in state["finished"]:
            state["finished"].append(skill_name)
        state["last_skill"] = skill_name
        self._save_state(state)
        self.write_log(f"✅ {skill_name} 执行成功并记录状态")
        return True

    def run_full_pipeline(self, skip_list: list[str] = None):
        """
        完整流水线入口
        :param skip_list: 需要跳过的技能列表，例如 ["B-Skill"]
        """
        if skip_list is None:
            skip_list = []

        self.write_log(f"本次流水线设置跳过技能：{skip_list if skip_list else '无'}")
        for skill in self.skill_info:
            s_name = skill["name"]
            # 如果在跳过列表，先标记跳过
            if s_name in skip_list:
                self.skip_skill(s_name)
            else:
                if not self.execute_skill(s_name):
                    self.write_log("流水线中断！")
                    return
        self.write_log("🎉 流水线执行完毕！")

    def reset_all(self):
        for f in self.runtime_dir.glob("*"):
            os.unlink(f)
        self.init_runtime()
        self.write_log("🔄 全部运行状态已重置，可以从头执行流水线")


if __name__ == "__main__":
    scheduler = SkillScheduler()
    scheduler.init_runtime()

    print("==== Skill统一调度器【支持跳过环节版本】====")
    print("1. 完整流水线（不跳过任何环节 A→B→C→D）")
    print("2. 完整流水线【跳过B-Skill】 A→(跳过B)→C→D")
    print("3. 单独执行A-Skill")
    print("4. 单独执行B-Skill")
    print("5. 单独执行C-Skill")
    print("6. 单独执行D-Skill")
    print("7. 手动标记跳过某个技能")
    print("9. 重置所有运行状态")
    opt = input("输入选项：")
    if opt == "1":
        scheduler.run_full_pipeline()
    elif opt == "2":
        # 示例：跳过B-Skill
        scheduler.run_full_pipeline(skip_list=["B-Skill"])
    elif opt == "3":
        scheduler.execute_skill("A-Skill")
    elif opt == "4":
        scheduler.execute_skill("B-Skill")
    elif opt == "5":
        scheduler.execute_skill("C-Skill")
    elif opt == "6":
        scheduler.execute_skill("D-Skill")
    elif opt == "7":
        name = input("请输入要跳过的技能名称(如 B-Skill)：")
        scheduler.skip_skill(name)
    elif opt == "9":
        scheduler.reset_all()
    else:
        print("无效选项")
