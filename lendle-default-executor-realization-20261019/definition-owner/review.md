# API3 Searcher profit 公开定义核验

结论：本轮取得官方当前部署前端的真实计算文本，已能确定按交易分组的前端算式；仍未取得后端字段生成源码，不能把该值认证为完整个人净利润。公开动作共 4/4，源码仅静态阅读，未执行或请求其数据服务。

1. **前端算式已证。** 官方入口 HTML 明确引用 `assets/index-ByjCsl3Q.js`。该 bundle 的 `hr0` 按 `txHash` 分组，将同一交易各清算条目的 `incentiveUsd` 相加，再减该组首条记录的 `gasCostUsd` 和 `bidAmountUsd`：`profitUsd = Σ(incentiveUsd) − gasCostUsd − bidAmountUsd`。两项费用在此函数中每个交易各扣一次。定位：原件第 517 行、0 基字节 3796599；结果字段在 3796949。这不是重新计算任何实际利润。

2. **实际使用路径与限制已证。** Lendle 配置没有专用页面，路由使用默认 `ike`，默认 schema 为 `LIt`，并实际调用 `hr0`。源码将清算数据位置列为 `https://oev-dashboard-backend-aws.api3.org/liquidations`，参数为 dApp；本轮没有访问这个位置。定位：第 525 行、字节 3926868 / 3933461，第 603 行、4396355。`LIt` 把 `collateralSeizedUsd`、`debtRepaidUsd`、`incentiveUsd`、`protocolFeeUsd` 等列为各自独立的输入（第 412 行、2817053）。因此不能从上述前端算式推出 `incentiveUsd` 必定等于抵押物估值减偿债估值；后端估值价格、时点、协议费处理以及费用字段来源仍为 **UNKNOWN**。该前端函数也没有另扣其他交易 hash 的失败支出；后端是否已作任何成本分摊仍为 **UNKNOWN**，不能宣称全部失败成本一定包含或一定排除。

3. **交换与借贷损益的排除已证。** `Searcher profit` 的提示明确将它称作估算，并说明不含清算中 swaps 与 loans 的损益估计（第 517 行、3790097）。据此，不能将正数直接称为变现后全费净额；但也不能因未核完整成本而抹去厂商已经发布的正估算。提示未细化具体 flashloan 费是否曾隐含于后端输入，该细项仍为 **UNKNOWN**。MEV/OEV/BFL 是字段标签，不能证明执行者是否为合作伙伴。

附带口径：当前 `Estimated OEV` 提示采用竞争拍卖和搜索者投入全部收入竞价的假设，并承认可能高估（第 517 行、3802076 的上下文）。它不是实际已支付拍卖收入的独立凭证，本轮未增加月份或全市场金额核算。

## 来源与版本

- [官方组织仓库列表](https://api.github.com/orgs/api3dao/repos?type=public&per_page=100&sort=full_name&direction=asc)：2026-10-19 15:28:49–15:28:53 UTC，HTTP 200，405282 B。该页 66 个公开仓库，未见分页链接；本轮没有确认与当前 OEV 看板对应的 GitHub 仓库/commit，不能据此断言源码不存在。
- [官方入口](https://oev-dashboard.api3.org/)：2026-10-19 15:28:49–15:28:50 UTC，HTTP 200，677 B。完整 HTML 保存为 `20261019T152823Z.02.source.html`。
- [入口实际引用的 bundle](https://oev-dashboard.api3.org/assets/index-ByjCsl3Q.js)：2026-10-19 15:29:44–15:29:45 UTC，HTTP 200，4396825 B。完整源码保存为 `20261019T152823Z.04.source.js.txt`，SHA256 `76fb5261842e70a5bc7b93d8298d9b4b4d0d0929d73574b37c11985dec6720d5`。发布日期、GitHub commit 和历史部署版本均 **UNKNOWN**；当前版本不能冒充历史月份当时运行的计算版本。

第 3 次公开动作同一 bundle 收到 HTTP 200/Content-Length 4396825，但本地 4 MiB 限额使 curl 以 56 退出、未取得正文。查询本地阻断记录后，第 4 次仅将同一 URL 的本地限额调整至 8 MiB，取得完整正文；未换身份、代理、协议或认证。失败元数据保留，不计为已读源码。来源均为普通 HTTPS 静态文本；TLS 校验结果为 0，无登录、源码执行、数据接口查询或收益核算。精确源码上下文及 0 基字节位置另存 `20261019T152823Z.04.final-evidence-excerpts.json`。

规则沿用已核 `PERMISSIONS-2026-10-14-v1` / `ROUTING-2026-10-13-v4`；实际 model/effort：**UNKNOWN**。本结论仅补强公开估算口径，不认证个人净盈利、容量或非伙伴复制资格。
