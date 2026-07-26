# A-Skill 环境初始化技能
## 公共来源配置：global_config.yaml
project_id、operator、server_env、memory_threshold、disk_threshold

## 独有业务
1. 加载global_config.yaml
2. 校验Python运行环境
3. 初始化runtime目录与状态文件
4. 写入系统环境信息到运行上下文
## 输出上下文
system_info、init_timestamp、init_finished
## 前置依赖：无
## 执行顺序：第一个
