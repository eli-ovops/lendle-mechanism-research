# 返回行地址关联补充

本次仅补必要的地址关联检查；原件、原receipt/QC/readme未改。

| 集 | 检查行 | 未关联行 | 关联字段 |
|---|---:|---:|---|
|E_normal|265|0|from / to / contractAddress|
|E_internal|0|0|空集，不可测试|
|E_erc20|119|0|from / to|
|X_normal|146|0|from / to / contractAddress|
|X_internal|0|0|空集，不可测试|
|X_erc20|544|0|from / to|

normal允许from/to/contractAddress，创建交易to为空不据此排除。ERC20只用from/to，不将token contractAddress当持有者关联。两个internal空集不能认证trace身份或完整内部路径。全部非空返回集通过本项关联；未关联行清单均为空。各源row文件SHA256及精确边界见JSON。仅核返回记录是否与请求地址直接关联，不证明经济主体、控制权或策略归属。无网络、无金额运算/值比较、无重复日期/费用QC。
