# 2026年9月E/X公开原记录获取

**完成固定六集的提供者分页原件获取及字段QC；不构成完整账户账或盈利验收。** 请求24/40，所有响应HTTP200（两次initialized通知202），没有来源拒绝、鉴权或限流。两端closest=before返回块100045244、101341244；查询均inclusive，再按每行1788220800≤timeStamp<1790812800筛9月。未发现本批区间外或时间缺失行；原行结构/页/行位置全部保留。

| 集 | 实际非空页 | 9月行 | 有效空末页 |
|---|---|---:|---:|
| E normal | 200、65 | 265 | page3 |
| E internal | 无；provider empty | 0 | page1 |
| E ERC20 | 119 | 119 | page2 |
| X normal | 146 | 146 | page2 |
| X internal | 无；provider empty | 0 | page1 |
| X ERC20 | 200、200、144 | 544 | page4 |

每个末页均为实际result[]、status0、No transactions found，原SSE/业务原文保留；没有把HTTP200、NOTOK、解析失败当空页。短页均补请求空末页。E normal与旧封存265条索引hash集完全一致；E/X normal各自hash唯一。 E/X normal交集146个hash、并集265个，X是否为E子集：True；两个列表不能相加当独立交易次数。合同创建行to可为空，按from/to/contractAddress关联，未因此误报非本人。宽区间边缘记录若存在会原样保留，本批边缘行计0。

**身份与字段限制：** 两个internal工具都只返回提供者空列表，traceId身份检查因无行而不可测试；这不能证明浏览器已提示的零值内部调用/内部revert不存在或完整调用树已覆盖。ERC20的119/544行全部缺logIndex；X包含68个父hash，各父hash多行，均保留，未按hash/相同值或看似重复内容去重。确切事件身份仍UNKNOWN，不能仅凭本服务行数声称完整链上Transfer日志。normal保留gasPrice、gasUsed、L1相关字段等原始字符串；没有乘积、费用合计或估值。仅保留付款者归费用原则，未对收款人分摊/扣费。

**本地中断与恢复：** 首匿名会话请求1–7已取得两块、E normal200+65及真实空末页。自有客户端把regex Match对象当bool写JSON，触发TypeError；不是限流或来源拒绝，会话标识未写盘。原件全部保留，修复为bool。第二会话已在Root收紧恢复前发出请求8–14（初始化、两块与E normal不必要重取），如实计入总预算，原始文件不覆写。Root澄清MCP会话不提供历史链一致性快照后，不再重取已完E/块，连续完成其余五集至请求24。最终E_normal.rows.json从首会话5–7本地恢复；第二会话E副本保存在E_normal-second-session.rows.json，其他五集来自请求15–24。必要一致项是同一来源、固定块区间、时间规则及分页，不是会话本身。

**产物：** 六个E/X_normal/internal/erc20.rows.json保存row原字段与source_page/source_row_1based/source_response、月份布尔标记；没有删行。逐请求*.request.json、*.response.sse、*.headers-safe.json、*.acquisition.json以及tool-data副本保留UTC、HTTP、哈希。安全头不含MCP会话标识/Set-Cookie；会话ID仅临时内存，进程退出即丢弃。固定参数先于请求写入fixed-parameters.json；session2记录原总预算未变。coverage-qc.json与offline-verification.json给出分页/身份/日期/字段QC与旧索引比较。

获取止于2026-10-19T16:30:49.021307+00:00；磁盘与RSS见acquisition-receipt.json，均低于64MiB/512MiB。没有注册、取key、安装、配置修改、被拒CSV/balance/IPFS访问，未调用区块链RPC、eth_call、trace或receipt代理；未执行来源JS/EVM/模型/回测/策略/交易或财务核算。只用官方keyless MCP四类公开记录/块时间工具。未触及排除目录、凭证或其他Owner文件。实际model/effort UNKNOWN。
