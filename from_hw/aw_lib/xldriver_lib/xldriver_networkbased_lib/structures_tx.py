from ctypes import Structure, c_uint, c_ushort, c_ubyte


class T_XL_ETH_FRAME(Structure):
    XL_ETH_PAYLOAD_SIZE_MAX = 1500
    _fields_ = [
        ("etherType", c_ushort),
        ("payload", c_ubyte * XL_ETH_PAYLOAD_SIZE_MAX),
    ]


class T_XL_ETH_FRAMEDATA(Structure):
    XL_ETH_RAW_FRAME_SIZE_MAX = 1600
    _fields_ = [
        ("ethFrame", T_XL_ETH_FRAME),
        ("rawData", c_ubyte * XL_ETH_RAW_FRAME_SIZE_MAX)
    ]


class T_XL_ETH_DATAFRAME_TX(Structure):
    XL_ETH_MACADDR_OCTETS = 6
    _fields_ = [
        ("frameIdentifier", c_uint),
        ("flags", c_uint),
        ("dataLen", c_ushort),
        ("reserved", c_ushort),
        ("reserved2", c_uint * 4),
        ("destMAC", c_ubyte * XL_ETH_MACADDR_OCTETS),
        ("sourceMAC", c_ubyte * XL_ETH_MACADDR_OCTETS),
        ("frameData", T_XL_ETH_FRAMEDATA)
    ]
