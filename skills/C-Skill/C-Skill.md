# C-Skill 数据校验清洗技能
## 公共来源配置：global_config.yaml
project_id、operator、memory_threshold、disk_threshold

## 独有业务
1. 加载global_config.yaml
2. 使用全局阈值对采集指标进行校验
3. 生成清洗后有效指标与校验结果
## 输出上下文
valid_metrics、check_result
## 前置依赖：B-Skill执行完成
