# 源码费用语义：固定公式与blob字段

本轮只读既存官方op-geth固定提交`c739e50e35071247cf459cbcbbbfc4cf989b4c57`源码，没有重新联网或执行Go／EVM。

执行Owner预检发现：全部265个回执的blobGasUsed非零，但交易类型为3笔legacy、262笔type2。不能把字段名字当作type3或额外费用的证明。

Root定向实读已存`lendle-historical-receipt-fee-fields-20261020/source-owner/07-ethapi-api-go.source` L1957–1963：Optimism非deposit回执中，DAFootprintGasScalar非nil时，Jovian把blobGasUsed复用于DA footprint。L1979–1981则单独在type为BlobTxType时输出blobGasPrice。`08-rollup-cost-go.source` L473–475起说明该DA占用用于区块限制及base-fee更新。本轮不能因此再按blobGasUsed加第四项费用，也不能把其非零写成类型预检失败。

独立方法Owner实读上述段落，以及rollup_cost.go L437–442的operator算式、state_transition.go L1050–1065按最终gas用量退款、state_processor.go L240–242把转换后费用赋给receipt.L1Fee，支持先作固定三账的条件一致性核验。没有独立认证当时主网节点二进制或逐块配置；方法可核不等于历史环境已独立认证。

既存explorer的spanTxFee提示只显式写包括operator费用，L1还有独立展示；是否与三项总和一致仍须用事前固定三账精确检验，不能从工具提示先行断定。若不符，保留差异并停止，不换公式、折算比例或选样。

以上是金额计算之前的方法依据；金额核算仍由execute-owner一次执行，Root不另跑一遍。
