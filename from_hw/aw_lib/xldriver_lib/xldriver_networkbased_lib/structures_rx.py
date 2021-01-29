from ctypes import Structure, c_ubyte, c_uint, c_ushort, c_uint64, Union


class T_XL_ETH_FRAME(Structure):
    XL_ETH_PAYLOAD_SIZE_MAX = 1500
    _fields_ = [
        ("etherType", c_ushort),
        ("payload", c_ubyte * XL_ETH_PAYLOAD_SIZE_MAX)
    ]


class T_XL_ETH_FRAMEDATA(Structure):
    XL_ETH_RAW_FRAME_SIZE_MAX = 1600
    _fields_ = [
        ("rawData", c_ubyte * XL_ETH_RAW_FRAME_SIZE_MAX),
        ("ethFrame", T_XL_ETH_FRAME)
    ]


class T_XL_NET_ETH_DATAFRAME_RX(Structure):
    XL_ETH_MACADDR_OCTETS = 6
    _fields_ = [
        ("frameDuration", c_uint),
        ("dataLen", c_ushort),
        ("reserved1", c_ubyte),
        ("reserved2", c_ubyte),
        ("errorFlags", c_uint),
        ("reserved3", c_uint),
        ("fcs", c_uint),
        ("destMAC", c_ubyte * XL_ETH_MACADDR_OCTETS),
        ("sourceMAC", c_ubyte * XL_ETH_MACADDR_OCTETS),
        ("frameData", T_XL_ETH_FRAMEDATA)
    ]


class T_XL_NET_ETH_DATAFRAME_RX_ERROR(Structure):
    XL_ETH_MACADDR_OCTETS = 6
    _fields_ = [
        ("frameDuration", c_uint),
        ("errorFlags", c_uint),
        ("dataLen", c_ushort),
        ("reserved1", c_ubyte),
        ("reserved2", c_ubyte),
        ("reserved3", c_uint * 2),
        ("fcs", c_uint),
        ("destMAC", c_ubyte * XL_ETH_MACADDR_OCTETS),
        ("sourceMAC", c_ubyte * XL_ETH_MACADDR_OCTETS),
        ("frameData", T_XL_ETH_FRAMEDATA)
    ]


class T_XL_NET_ETH_CHANNEL_STATUS(Structure):
    _fields_ = [
        ("link", c_uint),
        ("speed", c_uint),
        ("duplex", c_uint),
        ("mdiType", c_uint),
        ("activeConnector", c_uint),
        ("activePhy", c_uint),
        ("clockMode", c_uint),
        ("brPairs", c_uint)
    ]


class s_xl_eth_net_tag_data(Union):
    XL_ETH_EVENT_SIZE_MAX = 2048
    _fields_ = [
        ("rawData", c_ubyte * XL_ETH_EVENT_SIZE_MAX),
        ("frameSimRx", T_XL_NET_ETH_DATAFRAME_RX),
        ("frameSimRxError", T_XL_NET_ETH_DATAFRAME_RX_ERROR),
        ("frameSimTxAck", T_XL_NET_ETH_DATAFRAME_RX),  # T_XL_NET_ETH_DATAFRAME_SIMULATION_TX_ACK
        ("frameSimTxError", T_XL_NET_ETH_DATAFRAME_RX_ERROR),  # T_XL_NET_ETH_DATAFRAME_SIMULATION_TX_ERROR
        ("frameMeasureRx", T_XL_NET_ETH_DATAFRAME_RX),  # T_XL_NET_ETH_DATAFRAME_MEASUREMENT_RX
        ("frameMeasureRxError", T_XL_NET_ETH_DATAFRAME_RX_ERROR),  # T_XL_NET_ETH_DATAFRAME_MEASUREMENT_RX_ERROR
        ("frameMeasureTx", T_XL_NET_ETH_DATAFRAME_RX),  # T_XL_NET_ETH_DATAFRAME_MEASUREMENT_TX
        ("frameMeasureTxError", T_XL_NET_ETH_DATAFRAME_RX_ERROR),  # T_XL_NET_ETH_DATAFRAME_MEASUREMENT_TX_ERROR
        ("channelStatus", T_XL_NET_ETH_CHANNEL_STATUS)
    ]


class T_XL_NET_ETH_EVENT(Structure):
    _fields_ = [
        ("size", c_uint),
        ("tag", c_ushort),
        ("channelIndex", c_ushort),
        ("userHandle", c_uint),
        ("flagsChip", c_ushort),
        ("reserved", c_ushort),
        ("reserved1", c_uint64),
        ("timeStampSync", c_uint64),
        ("tagData", s_xl_eth_net_tag_data),
    ]
