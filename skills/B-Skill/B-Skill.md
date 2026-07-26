# B-Skill 资源数据采集技能
## 公共来源配置：global_config.yaml
project_id、operator、server_env、memory_threshold、disk_threshold

## 独有业务
1. 加载global_config.yaml
2. 读取A-Skill生成的运行上下文
3. 模拟采集内存、磁盘占用指标
## 输出上下文
resource_metrics、collect_finish_time
## 前置依赖：A-Skill执行完成
