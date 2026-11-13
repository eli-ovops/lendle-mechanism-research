# 创建交易input与当前runtime：静态身份补证

**已核：部署input含与当前封存runtime完全对应的模板，差异只在八个地址占位词；F21三处常量与构造器的直接常量写入结构吻合。** 初始CALLER写存储与浏览器标注的部署OwnershipTransferred事件也可定位。未执行/模拟EVM，不能把模板匹配当作构造路径执行证明、9月版本连续性或当前owner证明。

## 原件与完整提取

Root普通GET的[创建交易原页](https://mantlescan.xyz/tx/0xc07efee4fec47aeafd84ba439651061db98bf843fb5e8ab37c465f7296c716b4)显示Success、区块100741886、2026-09-17 03:01:24 UTC、From E=`0x57D8718f0d24DB1F3F6445337c8A0C24948d77c2`、Created X=`0x5483e9260d84b16ac5a32f2ceb333c762db74718`。本Owner零网络；其获取回执为2026-10-19 15:59:26–15:59:27 UTC、HTTP200、388952B，HTML SHA256 `d9d67313a4dc70249fb2729836108f32bba658c7d6846032f7e2eecead2527e6`。

从HTML第1242行`textarea#inputdata`及`span#rawinput`各提取完整hex，两者完全一致，且与静态文本185/186行两份全文一致。完整input为42272字符（含0x）、21135字节；已保存 `deployment-input.hex.txt`。解码字节SHA256 `30b540577182cbd45dd1d32d72171c33d6d13200d9faeb226e3e8af7c5e1f239`。实际人工读取创建身份、Input标签及事件0相邻正文；大hex以完整提取/字节对照覆盖，未冒称逐条读完全部26条日志。

## 1. runtime模板与metadata对照

Input字节偏移`0x0717`起有`0x4b38`（19256）字节模板，随后64字节尾词。构造器`0x055b PUSH2 4b38`、`0x0560 PUSH3 000717`及`0x0565 CODECOPY`提供相应的字面长度/偏移依据；没有执行这些指令。

封存runtime并非input中的未经修改连续子串。将当前runtime以下八个32字节词归零，才与input模板**逐字节完全一致**：

| runtime词首PC | 当前词末20字节（前12字节零） |
|---|---|
| `0x1b1f / 0x1f52 / 0x276d / 0x2aa0 / 0x40a2` | `753a327cf502d91226d42d44481b8377e4d35fd6` |
| `0x1ccc / 0x28a9 / 0x49c1` | `f21b5df58addd51c8f7984111c5831bdcf20e263` |

这些归一化位置来自构造器MSTORE前的实际偏移常量，不是将任意不匹配区删掉。模板及归一化runtime的SHA256均为 `22aa77b9e2e67be4b1a0d319c50791f664335713743274a10ba12993807b06f8`；当前原runtime字节SHA256仍为 `6255b20f0a952481705feaa5e5fb47d941565cc9cb88e02df73217966788beb7`。全部差异原字节在`comparison.json`。

末尾53字节（51字节CBOR及2字节长度）完全相同，保持前轮的solc字段0.8.24与IPFS multihash；未请求IPFS或任何网关。64字节尾词的角色没有ABI认证，不能擅称owner/费率参数。

## 2. F21常量来源：可定位的构造写入结构

- 构造器`0x00c6 PUSH20 f21b…e263`，后接`0x00db PUSH1 a0; 0x00dd MSTORE`。另一字面地址753a…5fd6在`0x00ae PUSH20`后写入`0x80`。
- 复制模板后，`0x058b PUSH1 a0; 0x058d MLOAD`，随后以`0x1ccc / 0x28a9 / 0x49c1`为偏移执行三处MSTORE（PC `0x0595 / 0x059c / 0x05a1`），继而`0x05a2 RETURN`；它们正好是当前runtime三处PUSH32即时数的词首。另一内存词`0x80`对应五处753a…地址。

这说明部署input文本具有将F21硬编码地址装入runtime占位词的**immutable样式构造结构**；F21来源不再只靠成功交易收款地址反推。没有源码，未确认Solidity变量名、业务定义、许可或费用条款；更不能据此认定F21由E控制或其收款可合并为E利润。

字面地址窗口`[0x00ae,0x00de)`原字节SHA256 `c3bf1286db12d513f27b85903f1b8f12697093e72389e0cef655be206dccca07`；复制/写词窗口`[0x055a,0x05a3)`为 `74b6641ef27035a6de7bc3f3acf76799986703da5a643f0800470c9ac18de5b5`。原字节及逐PC描述在`constructor-evidence-windows.json`。

## 3. 初始调用者与边界

`0x006a CALLER`后可见地址位掩码、SLOAD合并、`0x0078 SSTORE`；`0x0079 CALLER`后有包含topic `8be007…57e0`的LOG3。原页事件0（静态文本约224–253行）将其解码为OwnershipTransferred，previousOwner为零、newOwner为E。这支持**浏览器记录的初始所有权转移与initcode调用者写入形状一致**；本Owner未独立核ABI/receipt，未执行存储写入，也未完整恢复目标打包槽的业务定义。对应窗口`[0x0060,0x009f)`SHA256 `f24f792240755e58b3655062ad4c1fbd0614288b2cbef9bde77badf6c1f02982`。

部署者=E及初始事件**不证明当前owner仍为E**，也不证明当前或9月某地址一定通过helper X的调用者门槛。前轮权限发现只针对helper X该入口；不证明Lendle底层清算不开放、API3伙伴准入受阻，或个人不能另建合法执行器。当前封存runtime与部署模板一致的差异模式，也不证明中间从未变更代码/存储、9月30日精确状态或历史执行连续性。

**未核：** 独立链节点创建receipt/code、构造路径执行证明、完整源码/ABI、后续所有权与许可变更、历史存储、F21真实控制/分配权利及任何费率/净利。Sourcify既有404、exact IPFS CID429均沿用已停状态，没有重取/换网关。本轮仅自有静态文本/字节处理，零新网络、无EVM/源码编译/金融核算/模型/回测/交易/签名；仅写本creator-review目录，旧文件未改。实际model/effort：UNKNOWN。
