# Architecture

主流程：

1. preprocess_query
2. planner
3. route_experts
4. execute_experts
5. align_results
6. fuse_results
7. generate_response
8. write_case_if_success

全部模块插件化：

- experts
- tools
- models
- fusion
- cases
