# keyless与receipt证据边界：独立静态审阅

当前已读新增原件无实质冲突；**仅文档和匿名初始化通过，历史原账未取得/未验收。** 最终稿尚待核，以下三项是需要保留的边界，不是追加取数要求。

1. `root/mcp-doc.source.txt`第25–38、302–332行明确官方keyless无需key、有16个工具、单独限速且无PRO；normal/internal/token transfers、receipt、logs、block-by-time在可用表内。不能把两个网页工具403推广为所有免费来源拒绝，也不能继续把“keyless具体目录未知”当当前结论。初始化请求仅initialize，响应只含协议/能力/服务器2.4.0；HTTP200不证明历史账户请求成功、分页完成或September E/X账完整。来源说明也不能替代实际tools/list/参数与单工具响应。

2. 同一目录未列专门historical native/ERC20 balance工具。get_native_balance的历史参数没有在本材料展示；不能声称它必定支持或绝不支持历史。原官方账务指南的历史余额PRO边界没有被这个目录推翻；也不能由PRO推出一切公开历史余额方法都不存在。任何可能的归档/逐笔重建仍需独立范围和完整性证据，尚未执行。

3. `root/receipt-doc.source.txt`第138–151行将cumulativeGasUsed定义为区块内截至本交易的累计量，gasUsed才是该交易量；effectiveGasPrice是实际gas单价。文档以chain1例子展示常规receipt字段，未说明Mantle L1/operator费用的字段、历史适用范围或是否已含总费用；字段未列不证明费用为零，也不证明实际响应绝不提供额外字段。全成本不得只靠通用gas字段或错误累计量认证，且不得重复扣已经包含的费用。

已完整读取：mcp-doc源336行、receipt-doc源193行；各自获取回执各16行；initialize获取回执15行、请求1行、响应3行。未读账户数据或其他原账，未新增网络、工具调用、RPC、EVM、源码执行、模型、收益核算、key或配置改动；未进入排除目录。actual model/effort UNKNOWN。


## 最终稿与新本地原件审阅

最终稿1–71行已读，**受限通过，must_fix=[]**。第3、11–22、26–30行已将“文档/初始化”推进为两类历史记录实际返回，并正确限于各一条；普通交易E为to，不把其gas计为E支出。第14行与实际tools/list的16工具、native tag仅latest/earliest/pending相符，earliest未冒充九月期初。第38–50行保留L1/operator全费、资本流/资产负债和重建边界，净权益恒等式与费用去重正确；第56行只是下一步固定期原件获取与QC，不是全账或净利已通过。

新增解析件只读业务状态、记录数、身份字段、请求参数与schema相关字段；金额/gas原数值未作解释或计算。首次工具schema全量打印的中段被工具截断，故不声称逐项完整语义读完；随后仅定向核工具名称列表、native输入schema与两请求参数。原SSE响应未复读，也未重现网络调用。

最终稿SHA256：`e501e43c3b3a5eb38eb2fff13a022cc7cc1835d60a15449b603b93dc4fd9cf87`；9753B。审阅结束：2026-10-19T16:18:48.700008+00:00。
