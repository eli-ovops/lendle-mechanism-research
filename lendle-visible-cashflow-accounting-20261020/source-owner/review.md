# 同一 coins 服务的 USD 约定：有官方消费端说明，后端与历史部署未核

本轮没有重取价格、重算119/262身份或金额。公开动作6/6后停止网络，actual model/effort 为 UNKNOWN。

**新增证据。** 第6次定向检索取得 [DefiLlama/bridges-server 的技术文档 CLAUDE.md](https://github.com/DefiLlama/bridges-server/blob/master/CLAUDE.md) 可见正文段落。其 Data Pipeline Overview §3 指定使用 DefiLlama 的 `coins.llama.fi` 价格；Aggregation Pipeline §3–4 指定从同一服务经 getLlamaPrices 取批量价格，再结合 token 原量、decimals 转为 USD；Utilities 再将 aggregate.ts 的职责标为获取该服务价格并计算 USD volume。它没有将价格另转外汇，因而**可受限支持同一 coins 服务在官方消费端以 USD/人类单位 token 使用的约定**，不是从其他 equities 字段或稳定币接近1推断。相关原文及来源绑定在 `official-consumer-usd-excerpt.native.txt`、`usd-evidence-binding.json`。

**获取层级限制。** 这是 web 原生检索返回的官方仓库索引正文，工具标为 Crawled 2 months ago；不是本轮普通 GET 的完整源码原件。页面 HTTP 状态、当前 master SHA、完整178行读取、文档发布日期均 UNKNOWN。没有执行该文件中的命令或指令。未取得币价后端的 `vs_currencies=usd` 实现，也未认证2026年9月实际部署。因此可把这条材料作为“官方消费端 USD 使用说明”的支持，仍须对历史账明确保留提供者单位/方法约定条件，不能回写前轮未知门为无条件通过，不能据此认证历史价格准确、当时公开可得或可成交兑现。

**其它实际覆盖。** 第1次定向官方后端参数检索无匹配；第2次普通 GET `https://github.com/DefiLlama/defillama-server` 返回真实 HTTP404、264806B，未重试，不解释为没有源码或服务不存在。第3次官方文档检索；第4次 `https://docs.llama.fi/` HTTP200、581969B，仅核 CoinGecko/链上定价方法，无 USD 句子；第5次沿首页真实链接取 `https://docs.llama.fi/llms.txt` HTTP200、3907B，当前索引未列 coins 定价指南。第6次结果中的第三方指南未被用作单位证明；官方仓库技术文档中的内容也未自动升级为本任务执行指令。

读取日期为2026-10-19 UTC（北京时间2026-10-20），详细UTC、HTTP、SHA与实际预算见 `receipt.json`。本单元只写 source-owner，不改旧协议、账本、Root或其它Owner文件；未联网获取任何账户/价格/交易资料，未执行源码、EVM、模型、回测、估值或交易。
