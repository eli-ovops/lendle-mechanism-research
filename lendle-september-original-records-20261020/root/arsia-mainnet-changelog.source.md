> For the complete documentation index, see [llms.txt](https://docs.mantle.xyz/network/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://docs.mantle.xyz/network/for-node-operators/network-updates/changelogs/mantle-v2-v1.5.4-arsia-upgrade.md).

# Mantle v2 v1.5.4 - Arsia Upgrade

This release activates the **Arsia upgrade on Mantle Mainnet** and includes audit-driven fixes on top of the v1.5.3 Sepolia release.

Arsia is scheduled to activate on Mantle Mainnet at L2 block timestamp **1776841200** (Wednesday, **April 22, 2026, 07:00:00 UTC**).

{% hint style="info" icon="triangle-exclamation" %}
**🚧 All Mantle Mainnet node operators must upgrade to this release before the activation time. 🚧**
{% endhint %}

### What's New in v1.5.4 (vs v1.5.3)

#### mantle-v2

* **op-node:** Fixed `CheckL2GenesisBlockHash` to gracefully handle `NotFound` errors.
* **op-node:** Updated derivation pipeline data source and L1 retrieval logic; added blob format switch tests.
* **op-batcher:** Configuration and driver improvements.
* **op-service:** Fixes to crypto signature handling, HSM signer, backup sync client, and transaction manager.
* **op-chain-ops:** Genesis and mantle config fixes.
* **contracts:** Removed dead code from `GasPriceOracle` and `L1Block`; fixed `OperatorFeeVault`.
* **deps:** Bumped op-geth to v1.5.4, gnark-crypto to v0.18.1, Go toolchain to 1.24.13.
* **infra:** Dockerfile version bumps across op-batcher, op-node, op-proposer, and gas oracle.
* **tests:** Added EIP-1559 params tests, blob format switch tests, L1 retrieval tests, and `NotFound` tolerance tests.
* **audit:** Uploaded CertiK audit report for Mantle Arsia.

#### op-geth

* **Removed unused `tokenRatio` read in receipt generation:** `DeriveL1GasInfoMantle` no longer reads the `tokenRatio` storage slot, eliminating a redundant state access.
* **Fixed `EstimateTotalFee` block pinning for hash-based selectors:** Hash-based `blockNrOrHash` selectors are now preserved as-is (instead of being converted to a block number), maintaining `requireCanonical` semantics consistent with `EstimateGas`.
* **DA footprint enforcement in preconfirmation checker:** Added DA space validation before applying transactions in the preconf path, preventing preconfirmed transactions from being rejected at seal time due to insufficient DA capacity. DA footprint is now correctly accumulated and reset per block.
* **Hardened `makeEnv` state resolution:** Added nil checks for `parentBlock`, `state`, and `release` when resolving historical state, preventing potential panics during deep reorgs.
* **Removed premature `getBlobsV2RequestHit` metric increment** in the `GetBlobsV2` API.
* **Code cleanup:** Removed commented-out imports and reformatted error variable alignment in the preconf checker.
