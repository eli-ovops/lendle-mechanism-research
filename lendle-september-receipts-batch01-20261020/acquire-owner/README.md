# 固定32笔九月历史receipt原件获取

状态：COMPLETE_FIXED32_PROVIDER_RECEIPTS_IDENTITY_ONLY；取得并通过身份QC 32/32；HTTP 34/34；停止原因：无。

只使用事前固定next_fixed_hashes，显式chainid5000；未重取3份既有receipt或265索引。初始化与通知后单线程顺序读取，未重试/换身份。原SSE、请求、安全头、解析包、receipt原字段、UTC/HTTP/hash与逐笔QC保留。

未取得/未接受：0；具体hash见coverage-qc.json。业务ok与receipt执行status分开记录，status0不是获取失败。

QC仅核请求hash/链上下文、父块、from/to/creation地址、tx index/status/gas计量与normal原行等价；log仅核hash/块/索引/地址格式及重复身份，不解码金额。响应缺独立chainId时不冒称独立链认证。缺字段/null不补零。

付款归属保留三类例外路径：meta/sponsor分担；deposit/system特殊或免费记账；call/estimate跳过真实付款路径（不能当已发生链上付款证据）。未将样本分类为普通全额from付款，未合计费用、金额、估值、账户或利润。

这只是同提供者记录与normal行的一致性，不是9月历史软件部署、全月完整净账或策略可复制性认证。无直接节点RPC、eth_call/estimate/trace/EVM、来源脚本、模型/回测/交易；不读凭证/排除目录。会话标识仅内存，实际model/effort UNKNOWN。

离线补核：32笔effectiveGasPrice与normal.gasPrice、l1Fee与normal.L1FeesPaid仅作十六/十进制原量表示等价检查，全部一致；没有计算任何费用。gasUsed/effectiveGasPrice/l1Fee/l1GasUsed/l1GasPrice/operatorFeeScalar/operatorFeeConstant/tokenRatio在32笔中均存在且非null，详见QC字段矩阵；不由存在推全月齐全。所有log标识检查/同hash+logIndex重复检查通过，未解码data金额。
