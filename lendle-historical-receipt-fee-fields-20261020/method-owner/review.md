# 历史receipt费用字段：静态方法审阅

**三份固定历史原件、源码补充的解释边界与最终正文限界通过，must_fix=[]。** 零新网络；本轮15分钟截止2026-10-19 16:58:23 UTC。实际model/effort UNKNOWN。源码赋值解释以最终补充为准，不认证提供者历史运行版本、全月完整费用或净利润。最终意见见`final-review.md`及receipt.json绑定。

1. **先核历史原件身份与状态，不把数据响应当执行。** 实际`get_transaction_receipt` schema只接受txhash及chainid，省略链默认Ethereum 1，因此本轮必须显式5000；该工具及官方文档描述读取已发生交易的状态/gas/logs，不是eth_call、估费、模拟或发送交易。readOnly/destructive=false是正面范围证据，不是绕过来源403/429的依据。旧助手记录的no receipt proxy不新增用户审批门槛。HTTP成功须与业务状态、非空receipt、transactionHash、区块、from/to或创建地址及status核对；null可表示未知hash/待确认，不能当零费或失败。provider原件不自动等于独立节点复核。

2. **实际gas字段不等于Mantle完整网络费。** 官方receipt文档将gasUsed定义为该交易用量，effectiveGasPrice为实际gas单价；cumulativeGasUsed是区块内截至该交易的累计量，不能代替单笔用量。它们区别于估计gas/交易gas上限，但一般模式与chain1例子没有认证Mantle九月全部L1/operator费用。新增字段应逐字保留名称、原值格式、缺失/null/明确零的区别和历史网络/版本绑定，不能把未列字段当零。当前参数/测试网公式/新估计不能填历史账单；旧tooltip如已含operator，不能未经厘清再加一遍。本轮仅查定义与原始字段，不乘加、汇总或换算费用。

3. **receipt的局部完整性不升级为全期净利。** status0表示交易执行失败，不能据此抹掉它的网络成本；顶层Success也不证明没有内部回退。logs/logIndex可推进所选交易的事件身份，但不等于完整内部调用树、全部融资/偿债、全月所有receipt或完整经济主体账。必须区分顶层付款身份与收款人、跨E/X及多个事件的同一外层交易费用，防止重复扣。三个固定案例即使字段齐全，也不认证期初末完整资产/债权/负债、所有者资本流、链外运营成本、美元兑现或可复制优势。完整历史损益不需要私人选单规则；缺少私人规则不抹去已有历史收款。

当前实际读取：上单元`root/mcp-tools-list.parsed.json`仅receipt工具对象；`root/receipt-doc.source.txt`第5–50、53–84、133–151、158–189行（此前曾完整读该文档）。本轮fixed-source-probe、5动作获取索引、三请求及三获取回执完整；三parsed副本定向读身份、完整字段名与结构，未解释费用原值或logs.data金额。原始SSE哈希均匹配各获取回执，三份SSE的单一JSON payload与parsed对象整体相同，属于本地静态身份检查，不是数值费用核算或来源代码执行。没有重新采集、节点RPC/EVM、模型、回测、交易或凭证/排除目录访问，未改其他Owner文件。

三个固定请求与事前probe一致，均显式chain5000；成功和失败交易均E→X，状态分别0x1/0x0；部署为E发出、to=null、contractAddress=X、status0x1。全部MCP业务data为ok=true/result=非空receipt，不能要求沿用交易列表接口的data.status=1。获取索引为初始化200、通知202、三数据200；并非五次全200。probe保存于首次请求之前，选择的是既有成功/失败/部署案例，没有按本轮费用值选择。

三receipt均实际报告gasUsed、effectiveGasPrice、l1Fee、operatorFeeScalar、operatorFeeConstant、tokenRatio等非空hex字段；没有totalFee字段。不能再说历史receipt里没有operator参数，也不能把参数字段自动解释为已付operator金额或已认证全费。日志数量48/0/26；失败日志为空，只能记此receipt无持久化日志，不能用空集all=true认证其事件身份或否定内部尝试。成功/部署的logIndex字段存在只推进这些原件的事件定位，不替代完整事件语义、trace或全月重建。身份/字段结构及源hash见`original-field-bindings.json`。
