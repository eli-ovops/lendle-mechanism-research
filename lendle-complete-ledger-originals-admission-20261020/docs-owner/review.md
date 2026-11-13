# 官方历史原账能力：有限文档核验

**结论：Mantle 5000有免费API层；但现有文档不能认证“无需认证、免费公开原件已足以闭合2026年9月E/X净权益、资本流与全费用”。** 本轮仅文档6次公开动作，零账户API、key申请或账务计算。以下为现网页自述，不是2026年9月接口版本或实际取数成功证明；发布日期UNKNOWN，读取2026-10-19 UTC。

1. **链支持已核，不应误写Mantle整链付费。** [Supported Chains](https://docs.etherscan.io/supported-chains.md)原文第14行将Mantle Mainnet/5000对应free=true，第74、112行把该标志解释为免费层可用。此为静态读取公开文档组件，未执行JS。链层免费不等于每个接口免费、无认证或历史完整。官方索引第20行给注册并创建免费key的路径；第13行另披露keyless MCP仅16个只读工具、无PRO，具体工具覆盖本轮未核，未连接。

2. **关键期初末余额接口有明确付费门槛。** [Tax and Accounting](https://docs.etherscan.io/resources/tax-and-accounting.md)第22–49行列normal/internal/ERC20 transfers三类，示例均带API key和分页；不能仅normal索引代表全部资金流。第69、97行明确native及指定ERC20的历史余额为PRO、Standard及以上；第84行当前全部ERC20持仓列表亦同。免费层的精确速率、页数/结果上限、时间保留限额与这三类交易端点各自完整套餐矩阵未读细页，保留UNKNOWN。由此可否定“上述历史余额端点天然免费”的获取假设，不能推导所有免费历史余额来源都不存在。

3. **receipt全费及完整净权益仍缺证。** 官方索引第128行只定位[receipt文档](https://docs.etherscan.io/api-reference/endpoint/ethgettransactionreceipt.md)，本轮未读字段细页或Mantle L1/operator收费规范，故这些费用是否返回、适用时期和是否已包含在总费中均UNKNOWN；不能用通用gas字段冒充全费用。余额/转账即使取得，也还须闭合E与X的主体/资产负债边界、全部相关资产与债务、期初末区块、资本流分类及费用重复扣除问题；文档存在不证明这些原件已取得。Root另报两个网页工具403，仅作为Root事实，不在本Owner独立文档覆盖内，不建议换入口重取。

实际覆盖：action1标准支持链页35行；action2官方索引208行；action3/4原生Markdown读取失败（源HTTP UNKNOWN）；action5/6同URL普通GET均HTTP200，10519B/6156B全文可读。六次预算已用尽，不新增RPC、账户API或文档读取。原响应、传输回执及SHA见receipt.json；未执行来源代码/EVM/模型/回测/金融核算，未访问凭证、账户或排除目录。actual model/effort：UNKNOWN。
