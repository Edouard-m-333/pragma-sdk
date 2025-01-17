import logging
import random
from dataclasses import dataclass
from enum import Enum, unique
from typing import List, Literal, Optional

from starknet_py.net.full_node_client import FullNodeClient

from pragma.core.utils import felt_to_str, str_to_felt

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


ADDRESS = int
HEX_STR = str  # pylint: disable=invalid-name

# Network Types
DEVNET = "devnet"
TESTNET = "testnet"
SEPOLIA = "sepolia"
MAINNET = "mainnet"
SHARINGAN = "sharingan"
FORK_DEVNET = "fork_devnet"
PRAGMA_TESTNET = "pragma_testnet"

Network = Literal[
    "devnet",
    "testnet",
    "mainnet",
    "sharingan",
    "pragma_testnet",
    "fork_devnet",
    "sepolia",
]

CHAIN_IDS = {
    DEVNET: 1536727068981429685321,
    SHARINGAN: 1536727068981429685321,
    TESTNET: 1536727068981429685321,
    MAINNET: 23448594291968334,
    PRAGMA_TESTNET: 8908953246943201047421899664489,
    FORK_DEVNET: 1536727068981429685321,
    SEPOLIA: 393402133025997798000961,
}

CHAIN_ID_TO_NETWORK = {v: k for k, v in CHAIN_IDS.items()}

STARKSCAN_URLS = {
    MAINNET: "https://starkscan.co",
    TESTNET: "https://testnet.starkscan.co",
    SEPOLIA: "https://sepolia.starkscan.co",
    DEVNET: "https://devnet.starkscan.co",
    SHARINGAN: "https://sharingan-explorer.madara.zone",
    PRAGMA_TESTNET: "https://testnet.pragmaoracle.com/explorer",
    FORK_DEVNET: "https://devnet.starkscan.co",
}

PRAGMA_API_URL = "https://api.dev.pragma.build"

RPC_URLS = {
    MAINNET: [
        "https://starknet-mainnet.public.blastapi.io/rpc/v0_6",
    ],
    TESTNET: [
        "https://starknet-testnet.public.blastapi.io/rpc/v0_6",
    ],
    SEPOLIA: [
        "https://starknet-sepolia.public.blastapi.io/rpc/v0_6",
    ],
}


def get_rpc_url(network=TESTNET, port=5050):
    if network.startswith("http"):
        return network
    if network == TESTNET:
        random_index = random.randint(0, len(RPC_URLS[TESTNET]) - 1)
        return RPC_URLS[TESTNET][random_index]
    if network == SEPOLIA:
        random_index = random.randint(0, len(RPC_URLS[SEPOLIA]) - 1)
        return RPC_URLS[SEPOLIA][random_index]
    if network == MAINNET:
        random_index = random.randint(0, len(RPC_URLS[MAINNET]) - 1)
        return RPC_URLS[MAINNET][random_index]
    if network == SHARINGAN:
        return "https://sharingan.madara.zone"
    if network == PRAGMA_TESTNET:
        return "https://testnet.pragmaoracle.com/rpc"
    if network == DEVNET:
        return f"http://127.0.0.1:{port}/rpc"
    if network == FORK_DEVNET:
        return f"http://127.0.0.1:{port}/rpc"

    raise ClientException("Must provide a network name or an RPC URL.")


def get_client_from_network(network: str, port=5050):
    return FullNodeClient(node_url=get_rpc_url(network, port=port))


@dataclass
class ContractAddresses:
    publisher_registry_address: int
    oracle_proxy_addresss: int


CONTRACT_ADDRESSES = {
    DEVNET: ContractAddresses(0, 0),
    TESTNET: ContractAddresses(
        2408056700008799988274832007944460979526684291270693941276336026156441738630,
        3108238389225984732543655444430831893780207443780498125530192910262931411303,
    ),
    MAINNET: ContractAddresses(
        1035964020232444284030697086969999610062982650901949616270651804992179237909,
        1202089834814778579992154020333959781277480478747022471664051891421849487195,
    ),
    SEPOLIA: ContractAddresses(
        764259049439565269590387705502051444787910047543242149334355727309682685773,
        1526899943909931281366530977873767661043021921869578496106478460498705257242,
    ),
    SHARINGAN: ContractAddresses(0, 0),
    PRAGMA_TESTNET: ContractAddresses(0, 0),
    FORK_DEVNET: ContractAddresses(0, 0),
}


@unique
class AggregationMode(Enum):
    MEDIAN = "Median"
    AVERAGE = "Mean"
    ERROR = "Error"

    def serialize(self):
        return {self.value: None}


@unique
class RequestStatus(Enum):
    UNINITIALIZED = "UNINITIALIZED"
    RECEIVED = "RECEIVED"
    FULFILLED = "FULFILLED"
    CANCELLED = "CANCELLED"
    OUT_OF_GAS = "OUT_OF_GAS"

    def serialize(self):
        return {self.value: None}


class Currency:
    id: int
    decimals: int
    is_abstract_currency: bool
    starknet_address: int
    ethereum_address: int

    def __init__(
        self,
        id_,
        decimals,
        is_abstract_currency,
        starknet_address=None,
        ethereum_address=None,
    ):
        if isinstance(id_, str):
            id_ = str_to_felt(id_)
        self.id = id_  # pylint: disable=invalid-name

        self.decimals = decimals

        if isinstance(is_abstract_currency, int):
            is_abstract_currency = bool(is_abstract_currency)
        self.is_abstract_currency = is_abstract_currency

        if starknet_address is None:
            starknet_address = 0
        self.starknet_address = starknet_address

        if ethereum_address is None:
            ethereum_address = 0
        self.ethereum_address = ethereum_address

    def serialize(self) -> List[str]:
        return [
            self.id,
            self.decimals,
            self.is_abstract_currency,
            self.starknet_address,
            self.ethereum_address,
        ]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "decimals": self.decimals,
            "is_abstract_currency": self.is_abstract_currency,
            "starknet_address": self.starknet_address,
            "ethereum_address": self.ethereum_address,
        }

    def __repr__(self):
        return f"Currency({felt_to_str(self.id)}, {self.decimals}, {self.is_abstract_currency}, {self.starknet_address}, {self.ethereum_address})"


class Pair:
    id_: int
    quote_currency_id: int
    base_currency_id: int

    def __init__(self, id_, quote_currency_id, base_currency_id):
        if isinstance(id_, str):
            id_ = str_to_felt(id_)
        self.id = id_  # pylint: disable=invalid-name

        if isinstance(quote_currency_id, str):
            quote_currency_id = str_to_felt(quote_currency_id)
        self.quote_currency_id = quote_currency_id

        if isinstance(base_currency_id, str):
            base_currency_id = str_to_felt(base_currency_id)
        self.base_currency_id = base_currency_id

    def serialize(self) -> List[str]:
        return [self.id, self.quote_currency_id, self.base_currency_id]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "quote_currency_id": self.quote_currency_id,
            "base_currency_id": self.base_currency_id,
        }

    def __repr__(self):
        return f"Pair({felt_to_str(self.id)}, {felt_to_str(self.quote_currency_id)}, {felt_to_str(self.base_currency_id)})"


DataTypes = Enum("DataTypes", ["SPOT", "FUTURE", "OPTION"])


class DataType:
    data_type: DataTypes
    pair_id: int
    expiration_timestamp: Optional[int]

    def __init__(self, data_type, pair_id, expiration_timestamp):
        if isinstance(pair_id, str):
            pair_id = str_to_felt(pair_id)
        elif not isinstance(pair_id, int):
            raise TypeError(
                "Pair ID must be string (will be converted to felt) or integer"
            )
        self.pair_id = pair_id

        self.data_type = DataTypes(data_type)
        self.expiration_timestamp = expiration_timestamp

    def serialize(self) -> dict:
        if self.data_type == DataTypes.SPOT:
            return {"SpotEntry": self.pair_id}
        if self.data_type == DataTypes.FUTURE:
            return {"FutureEntry": (self.pair_id, self.expiration_timestamp)}
        return {}

    def to_dict(self) -> dict:
        return {
            "pair_id": self.pair_id,
            "expiration_timestamp": self.expiration_timestamp,
            "data_type": self.data_type.name,
        }


class BasePragmaException(Exception):
    message: str

    def __init__(self, message: str):
        self.message = message

    def serialize(self):
        return self.message


class UnsupportedAssetError(BasePragmaException):
    pass


class ClientException(BasePragmaException):
    pass


class PoolKey:
    # token0 is the the token with the smaller adddress (sorted by integer value)
    # token1 is the token with the larger address (sorted by integer value)
    # fee is specified as a 0.128 number, so 1% == 2**128 / 100
    # tick_spacing is the minimum spacing between initialized ticks, i.e. ticks that positions may use
    # extension is the address of a contract that implements additional functionality for the pool
    token_0: int
    token_1: int
    fee: int
    tick_spacing: int
    extension: int

    def __init__(
        self,
        token_0: int,
        token_1: int,
        fee: int,
        tick_spacing: int,
        extension: int = 0,
    ):
        self.token_0 = token_0
        self.token_1 = token_1
        self.fee = fee
        self.tick_spacing = tick_spacing
        self.extension = extension

    def serialize(self) -> List[str]:
        return [
            self.token_0,
            self.token_1,
            self.fee,
            self.tick_spacing,
            self.extension,
        ]

    def to_dict(self) -> dict:
        return {
            "token_0": self.token_0,
            "token_1": self.token_1,
            "fee": self.fee,
            "tick_spacing": self.tick_spacing,
            "extension": self.extension,
        }

    def __repr__(self):
        return f"PoolKey({self.token_0}, {self.token_1}, {self.fee}, {self.tick_spacing}, {self.extension})"
