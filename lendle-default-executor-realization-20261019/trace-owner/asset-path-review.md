# 单笔资产路径：aToken已赎回为mETH，未证美元兑现或完整净利

**限定结论：已保存的Mantlescan HTML支持这笔交易完成清算、收到aToken后赎出底层mETH，并向sender转入mETH。它没有证明美元已兑现、sender拥有执行合约、全资产余额或全部成本闭合。** 合约名称、代币名称和事件解码来自explorer；独立ABI、官方部署注册表及节点receipt仍未认证。

固定原件URL：<https://mantlescan.xyz/tx/0x5165cdcf3363042ec3f6c4c04e64df1a6378dfeb47acfce978560433722e1507>。复用旧`receipt-owner/action2-mantlescan.source.html`，SHA256 `b0174b9a078a8957d32aaf4f81441a38f4e1e331cc5c9b13d3dcc0d59a80ca06`；静态文本SHA256 `e786385cb4203442f0a8e02e7ae1c933d326e202e8acd2fab7ff90478231b6f6`。本轮零新网络。

为便于定位，下称sender为`0x57D8718f0d24DB1F3F6445337c8A0C24948d77c2`，执行合约X为`0x5483e9260d84b16ac5a32f2CEB333C762dB74718`，被清算用户U为`0x29D54f612660b8052B82115CE9e095a7C9df4372`，交换事件地址S为`0x94d692aFff21E045691971A20DF4A9adb482DDF6`。以下编号均为页面事件表0—47的条目号，不冒充另取RPC的logIndex。

1. **偿债与收抵押物者是X，不能默认为sender自有本金。** #0显示S向X转WETH；#25显示X向`0x787Cb0D29194f0fAcA73884C383CF4d2501bb874`转WETH。#14/15记录U的债务token销毁，#26清算事件把debtAsset列为WETH、collateralAsset列为mETH、liquidator列为X、receiveAToken=True。#21/22则显示U向X转`0x0e927Aa52A38783C1Fd5DfA5c8873cbdBd01D2Ca`所代表的lvMETH。这支持该次偿债/清算份额的路径，不证明U全部债务清零。（静态文本L536—572、L1055—1122、L1325—1401、L1469—1566。）

2. **aToken之后确有底层资产赎出，不只停在aToken记账。** #38是mETH token `0xcDA86A272531e8640cD7F1a92c01839911B90bb0`从lvMETH地址转给X；#39为X的lvMETH转往零地址；#41 Withdraw的reserve=mETH、user/to均为X。#40另有Burn，但explorer把其字段命名为amountPYToRedeem/amountSyOut；未独立核ABI，保留原字段而不据名称推另一笔收益。上述Transfer与Withdraw的组合支持赎回底层mETH。（L1983—2142。）

3. **sender收到mETH，但经济归属和余额没有闭合。** #43记录X把mETH转向S；#44另转给`0xF21B5Df58AdDD51c8F7984111c5831BdcF20e263`；#45转给sender。没有把这三笔相加或与入项相减。F21地址的控制者、款项性质及是否同一主体未知，不能先称平台费、OEV分成或sender利润。X的控制权、起末存量和其他资产未核；#42/#46未解码原事件全部保留。LEND铸造/Staked及其他地址的余额事件也不能并入sender收入；其中Staked用户`0x5701eB87672D031dae5f5908d4C896717345Af1f`与sender不同。（#3—37及L2143—2322。）

4. **存在交换事件及可见费用原字段；未证独立闪电贷及其费率。** #47由S发Swap，sender/recipient均为X；amount0/amount1的原有正负号保留，不能当sender净收益。protocolFeesToken0=`9576225620`、protocolFeesToken1=`0`为原字段，未转换精度、估费率或推总成本，token0/1对应关系也未另取池getter确认。先由S付WETH、后向S付mETH的顺序与交换回调融资相容，这是推断；48条解码日志中未见名为FlashLoan的事件，不等于排除了所有信用/回调路径或证明借款费用为零。（#0/#43/#47，L2323—2388。）

5. **不能证明美元兑现。** 本笔可见路径支持底层mETH实际到账sender，未显示美元/美元稳定币兑出或银行入账。页面美元栏是explorer估值，不能当现金兑付；页面MNT网络费也未与mETH收款跨币种相减。可以确认token路径，不能据此确认完整净数量、净利润、持续盈利或容量。

**实际覆盖：** 已逐条读完19条All Transfers与48条Receipt Event Logs（0—47），完整保留含两个未解码条目42/46；没有删除激励、授权、状态或协议内部事件。仅保留Net Transfers显示作原件上下文，未采用其净额作为本Owner核算结果。静态页只有“279 zero value Internal Transactions”的Advanced链接与提示，没有279条逐调用明细；未读/未取调用树、内部失败明细、起末状态或外部账户历史，不能称内部流全覆盖。页面顶层Success亦不消除其内部revert提示。

`receipt-events.all.json`保留48条原样静态记录和逐条行号；`token-transfers.all.json`保留19条Transfer的token/from/to/raw value，不聚合；原HTML L1970—2807另存`receipt-events.all.raw-fragment.html`。全部输入/输出哈希在`static-index-receipt.json`，读取范围与边界在`read-receipt.json`。只运行自有静态索引/哈希，不执行来源JS/合约、EVM/RPC、模型、回测、交易或金额乘加；未触及凭证、其他交易、排除目录或他人文件。actual model/effort UNKNOWN。
