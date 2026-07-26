import json
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path


class SkillScheduler:
    def __init__(self, base_dir: Path = None):
        # 根目录初始化
        self.base_dir = base_dir if base_dir else Path(__file__).parent
        self.runtime_dir = self.base_dir / "runtime"
        self.state_file = self.runtime_dir / "execution_state.json"
        self.log_file = self.runtime_dir / "run.log"

        # Skill顺序定义（和原来保持一致）
        self.skill_info = [
            {
                "name": "A-Skill",
                "script": self.base_dir / "skills/A-Skill/skill_a.py"
            },
            {
                "name": "B-Skill",
                "script": self.base_dir / "skills/B-Skill/skill_b.py"
            },
            {
                "name": "C-Skill",
                "script": self.base_dir / "skills/C-Skill/skill_c.py"
            },
            {
                "name": "D-Skill",
                "script": self.base_dir / "skills/D-Skill/skill_d.py"
            }
        ]

    def init_runtime(self):
        """初始化运行目录与状态文件"""
        self.runtime_dir.mkdir(exist_ok=True)
        if not self.state_file.exists():
            init_state = {"finished": [], "last_skill": None}
            self._save_state(init_state)

    def _load_state(self):
        """私有方法：读取状态"""
        with open(self.state_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_state(self, state):
        """私有方法：保存状态"""
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def write_log(self, msg: str):
        """统一日志输出"""
        t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{t}] {msg}\n"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(line)
        print(line.strip())

    def can_run_skill(self, target_name: str) -> tuple[bool, str]:
        """校验是否允许执行目标技能"""
        state = self._load_state()
        finished = state["finished"]

        # 找到目标技能索引
        target_idx = -1
        for idx, skill in enumerate(self.skill_info):
            if skill["name"] == target_name:
                target_idx = idx
                break
        if target_idx == -1:
            return False, f"不存在技能：{target_name}"

        # 遍历前置技能校验
        pre_skills = self.skill_info[:target_idx]
        for pre in pre_skills:
            if pre["name"] not in finished:
                return False, f"前置技能【{pre['name']}】未执行，不能运行{target_name}"
        return True, "允许执行"

    def execute_skill(self, skill_name: str) -> bool:
        """执行单个skill"""
        ok, msg = self.can_run_skill(skill_name)
        if not ok:
            self.write_log(f"❌ {msg}")
            return False

        skill_item = next(s for s in self.skill_info if s["name"] == skill_name)
        script_path = str(skill_item["script"])
        self.write_log(f"===== 启动 {skill_name} 脚本：{script_path} =====")

        # 调用独立python脚本
        ret = subprocess.run([sys.executable, script_path])
        if ret.returncode != 0:
            self.write_log(f"❌ {skill_name} 执行异常，返回码：{ret.returncode}")
            return False

        # 更新执行状态
        state = self._load_state()
        if skill_name not in state["finished"]:
            state["finished"].append(skill_name)
        state["last_skill"] = skill_name
        self._save_state(state)
        self.write_log(f"✅ {skill_name} 执行成功并记录状态")
        return True

    def reset_all(self):
        """清空运行时状态，重置流水线"""
        for f in self.runtime_dir.glob("*"):
            os.unlink(f)
        self.init_runtime()
        self.write_log("🔄 全部运行状态已重置，可以从头执行流水线")

    def run_full_pipeline(self):
        """一键完整串行流水线 A→B→C→D"""
        for skill in self.skill_info:
            if not self.execute_skill(skill["name"]):
                self.write_log("流水线中断！")
                return
        self.write_log("🎉 完整流水线 A→B→C→D 全部执行完毕！")


if __name__ == "__main__":
    # 实例化调度器
    scheduler = SkillScheduler()
    scheduler.init_runtime()

    print("==== Skill统一调度器【Class版本】====")
    print("1. 一键完整流水线 A→B→C→D")
    print("2. 单独执行A-Skill")
    print("3. 单独执行B-Skill")
    print("4. 单独执行C-Skill")
    print("5. 单独执行D-Skill")
    print("9. 重置所有运行状态")
    opt = input("输入选项：")
    if opt == "1":
        scheduler.run_full_pipeline()
    elif opt == "2":
        scheduler.execute_skill("A-Skill")
    elif opt == "3":
        scheduler.execute_skill("B-Skill")
    elif opt == "4":
        scheduler.execute_skill("C-Skill")
    elif opt == "5":
        scheduler.execute_skill("D-Skill")
    elif opt == "9":
        scheduler.reset_all()
    else:
        print("无效选项")
