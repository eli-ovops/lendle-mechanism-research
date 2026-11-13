# Batch01独立方法准备

本文件为准备时的方法记录；当前最终验收见final-review.md及receipt.json。Owner只写method-owner，本轮零网络、15分钟自2026-10-19 16:56:31 UTC至17:11:31 UTC，actual model/effort UNKNOWN。

1. 独立只读核固定scope源hash、265身份行排序、扣除3已得哈希后的首32，不读取金额字段。三个排序数值仅是时间戳/区块号/交易序号；不是费用或收益计算。获取后逐件核请求chain5000/hash、原SSE及source SHA与解析对象等价、非null receipt、父交易/区块/状态身份及预定清单覆盖。null/业务错误保留缺件，不补零或按新结果换样本。

2. 字段验收区分缺失、null、空串及明确零。zero-valued operator参数不等于缺失，也不自动证明费用为零。日志非空时核父hash/blockHash/logIndex及唯一身份；空日志只标不适用，不把空集all=true升级为事件完整。单批字段/机器QC不替代原件语义、版本与实际包含关系核验。

3. 费用只按实际付款与同一外层交易归集身份；E地址命中不等于E全额承担费，赞助分支待分类，同hash跨地址/多事件不能重复扣。L1Fee已转换的固定源码路径不再重复乘TokenRatio，operator参数不直接当实付金额。32新收据/累计35份不推全月265覆盖、完整资本流/资产负债、净利润、美元兑现或个人可复制优势。所有本轮费用/收益乘加、RPC/EVM、模型/回测/交易与凭证/排除目录访问均不执行。

固定清单准备核验已通过：E源SHA与scope相符；仅投影265条hash/timeStamp/blockNumber/transactionIndex身份字段，升序并扣除3已得后的首32与冻结清单逐位相同；全排序摘要的带末尾换行编码也匹配。详见preparation-selection-check.json。这不代表32笔已取得。

原生赞助补证：已完整静态读同commit的meta_transaction.go。DynamicFeeTx、data长度>32及精确32字节MetaTxPrefix是所读解码路径的必要条件。Root报告同封存E源265个合法input均不匹配该前缀，可在“固定源码+该提供者既有input”的范围关闭笼统MetaTxParams未知；本Owner核源hash及summary，不重扫全部input、不执行RLP/签名或来源代码。该结论不认证历史二进制，也不排除deposit/system等其他路径、链上/链外补偿或回款；不能将其扩大为无任何形式代付。
