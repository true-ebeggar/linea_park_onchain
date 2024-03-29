
class BlockchainNetwork:
    def __init__(self, rpc, scan, token, chain_id):
        self.rpc = rpc
        self.scan = scan
        self.token = token
        self.chain_id = chain_id


# Creating instances for each network
arbitrum = BlockchainNetwork("https://rpc.ankr.com/arbitrum", "https://arbiscan.io/tx/", "ETH", 42161)
linea = BlockchainNetwork('https://1rpc.io/linea', 'https://lineascan.build/tx/', 'ETH', 59144)
zora = BlockchainNetwork('https://rpc.zora.energy', 'https://explorer.zora.energy/tx/', 'ETH', 7777777)
arbitrum_nova = BlockchainNetwork("https://nova.arbitrum.io/rpc", "https://nova.arbiscan.io/tx/", "ETH", 42170)
avalanche = BlockchainNetwork("https://rpc.ankr.com/avalanche", "https://snowtrace.io/tx/", "AVAX", 43114)
bsc = BlockchainNetwork("https://rpc.ankr.com/bsc", "https://bscscan.com/tx/", "BNB", 56)
bsc_testnet = BlockchainNetwork("https://data-seed-prebsc-1-s1.binance.org:8545", "https://testnet.bscscan.com/tx/", "tBNB", 97)
celo = BlockchainNetwork("https://rpc.ankr.com/celo", "https://celoscan.io/tx/", "CELO", 42220)
combo_testnet = BlockchainNetwork("https://test-rpc.combonetwork.io", "https://combotrace-testnet.nodereal.io/tx/", "tcBNB", 91715)
core = BlockchainNetwork("https://rpc.coredao.org", "https://scan.coredao.org/tx/", "CORE", 1116)
dfk = BlockchainNetwork("https://subnets.avax.network/defi-kingdoms/dfk-chain/rpc", "https://explorer.dfkchain.com/tx/", "JEWEL", 53935)
eth = BlockchainNetwork("https://rpc.ankr.com/eth", "https://etherscan.io/tx/", "ETH", 1)
fantom = BlockchainNetwork("https://rpc.ankr.com/fantom", "https://ftmscan.com/tx/", "FTM", 250)
gnosis = BlockchainNetwork("https://rpc.ankr.com/gnosis", "https://gnosisscan.io/tx/", "xDAI", 100)
harmony = BlockchainNetwork("https://api.harmony.one", "https://explorer.harmony.one/tx/", "ONE", 1666600000)
klaytn = BlockchainNetwork("https://1rpc.io/klay", "https://scope.klaytn.com/tx/", "KLAY", 8217)
mantle = BlockchainNetwork("https://mantle.publicnode.com", "https://explorer.mantle.xyz/tx", "MNT", "5000")
metis = BlockchainNetwork("https://andromeda.metis.io/?owner=1088", "https://andromeda-explorer.metis.io", "METIS", 1088)
moonbeam = BlockchainNetwork("https://rpc.ankr.com/moonbeam", "https://moonscan.io/tx/", "GLMR", 1284)
moonriver = BlockchainNetwork("https://moonriver.public.blastapi.io", "https://moonriver.moonscan.io/tx/", "MOVR", 1285)
op_bnb_mainet = BlockchainNetwork("https://opbnb-mainnet-rpc.bnbchain.org", "https://opbnbscan.com/tx/", "BNB", 204)
op_bnb_testnet = BlockchainNetwork("https://opbnb-testnet-rpc.bnbchain.org", "https://opbnbscan.com/tx/", "tBNB", 5611)
optimism = BlockchainNetwork("https://rpc.ankr.com/optimism", "https://optimistic.etherscan.io/tx/", "ETH", 10)
polygon = BlockchainNetwork("https://rpc.ankr.com/polygon", "https://polygonscan.com/tx/", "MATIC", 137)
polygon_zkevm = BlockchainNetwork("https://zkevm-rpc.com", "https://zkevm.polygonscan.com/tx/", "ETH", 1101)
zk_sync = BlockchainNetwork("https://zksync.meowrpc.com", "https://explorer.zksync.io/tx/", "ETH", 324)

# Encapsulating all networks in a class
class AllNetworks:
    def __init__(self):
        self.arbitrum = arbitrum
        self.zora = zora
        self.linea = linea
        self.arbitrum_nova = arbitrum_nova
        self.avalanche = avalanche
        self.bsc = bsc
        self.bsc_testnet = bsc_testnet
        self.celo = celo
        self.combo_testnet = combo_testnet
        self.core = core
        self.dfk = dfk
        self.eth = eth
        self.fantom = fantom
        self.gnosis = gnosis
        self.harmony = harmony
        self.klaytn = klaytn
        self.mantle = mantle
        self.metis = metis
        self.moonbeam = moonbeam
        self.moonriver = moonriver
        self.op_bnb_mainet = op_bnb_mainet
        self.op_bnb_testnet = op_bnb_testnet
        self.optimism = optimism
        self.polygon = polygon
        self.polygon_zkevm = polygon_zkevm
        self.zk_sync = zk_sync

# Creating an instance of AllNetworks
all = AllNetworks()
