# 固定历史价格覆盖：有限静态验收

**受限通过，must_fix=[]。** 最终正文60行已完整实读；SHA256 `2b7d9b2d6b0d255a27f72de3fba4dcc85fa5125cc6876600ab32d627831d6cf1`。

- L5–18正确报告119收款／262费用共381事件均有合格时间窗候选；376返回行、227个唯一资产／价格时点、实际188个共享观察没有冒称381个独立样本。完整覆盖来源于Source Owner封存的全量匹配QC，本Owner未重做全381匹配。
- L24–34与报价前冻结协议一致：一小时既往窗口、中点单次请求、新返回候选池最大u、冲突／非法不回退、旧pilot隔离、confidence不择价。窗口是会计约定，不能证明当时公开可得或可成交；未因新结果改门槛。
- L38–58准确保留单位和经济边界：官方规范已支持真实server／batch schema及适配定价机制；精确contract key不等于成交价。USD单位未获明文，不抹去381个价格／时间匹配，但不能据此算美元主账。batch无decimals，可另引用既有精度并明示层级；不必先查完所有赎回关系。末端已反映的内部偿债／交换／F21不重复扣；拟议历史标价差额不冒完整利润、兑现或未来复制结论。

本Owner实际独立覆盖：旧final全文及旧receipt相关字段；当前protocol原35行及报价前新增3字段；376请求元数据有序唯一／协议绑定；五批请求与固定376对恰好一致、五原体hash／size与回执相符；官方spec的current／chart／batch三个完整原文片段字节相符；按报价值读取前固定的首MNT、末ERC20、默认mETH三样本，静态核其窗口内最大u及对应原字段。Source Owner报告全文、获取回执和coverage-qc摘要均已读，没有冒称独立核查所有381条或整个39文件manifest。

本Owner零网络、价格或金额加减乘除／数量费用重算／估值净利、来源代码或EVM执行、模型／回测／交易／外发；未读凭证或排除私人目录。初次precheck旧hash断言发生于写入前，实因为Root报价前澄清协议；诊断及新绑定已保留，未重跑取源。细节见precheck-receipt.json、source-and-fixed-samples-review.json及最终receipt.json。actual model/effort UNKNOWN；统一截止2026-10-19 18:56:10 UTC。
