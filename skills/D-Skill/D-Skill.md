# D-Skill 报告生成 & 任务收尾技能
## 公共来源配置：global_config.yaml
project_id、operator、server_env

## 独有业务
1. 加载global_config.yaml
2. 读取C-Skill校验结果
3. 生成最终汇总报告，标记项目完成
## 输出上下文
final_report、project_status
## 前置依赖：C-Skill执行完成
