import struct
import msgpack
import hashlib
import pyshark
import asyncio
from enum import Enum
from loguru import logger

class PktType(Enum):
    Ack = 1
    SessionConfig = 2
    Data = 3

class Channel(Enum):
    Protobuf = 1
    Data = 2
    Activity = 5

class OpCode(Enum):
    Plain = 1
    Encrypted = 2

class MassDataType(Enum):
    WATCHFACE = 16
    FIRMWARE = 32
    NotificationIcon = 50
    ThirdpartyApp = 64

class MiPacket:

    def __init__(self, pkt_type, seq, checksum, data):
        self.pkt_type = pkt_type
        self.seq = seq
        self.checksum = checksum
        self.data = data

async def capture_cleanup(process):
    if process.returncode is None:
        try:
            process.kill()
            return await asyncio.wait_for(process.wait(), 1)
        except:
            pass

def crc16(data: bytes, poly: int = 0xA001, init_value: int = 0x0000) -> int:
    crc = init_value
    for byte in data:
        crc ^= byte  # 将当前字节与CRC值异或
        for _ in range(8):  # 对每一位进行处理
            if crc & 0x0001:  # 判断最低位
                crc = (crc >> 1) ^ poly  # 右移并与多项式异或
            else:
                crc >>= 1  # 右移
    return crc & 0xFFFF  # 只取最低16位

class WireSharkError(Exception):

    def __init__(self):
        pass

class MiCapture:

    def __init__(self, file_name):

        # 手机 => 手表
        self.p2w_packets = []
        self.p2w_buffer = b'' 

        # 手表 => 手机
        self.w2p_packets = []
        self.w2p_buffer = b'' 

        self.capture = pyshark.FileCapture(file_name)

        # 启用调试模式
        # self.capture.set_debug()

        # 自定义cleanup抑制崩溃
        self.capture._cleanup_subprocess = capture_cleanup

        self.succ = self.decode()

        self.capture.close()

    def find_watch_addr(self):

        for packet in self.capture:
            if 'BTHCI_ACL' not in packet:
                continue

            name = packet.bthci_acl.src_name
            bd_addr = packet.bthci_acl.src_bd_addr

            if ('Watch' in name or 'Band' in name) and ('Xiaomi' in name or 'REDMI' in name):
                self.name = name
                self.bd_addr = bd_addr
                return True
        
        return False

    def decode(self):
        if self.find_watch_addr():
            logger.info("已经搜索到设备 设备名: %s 地址: %s" % (self.name, self.bd_addr))

            logger.info("正在重组数据包...")

            for packet in self.capture:

                # 过滤杂包
                if 'BTSPP' not in packet: continue
                
                # 按地址过滤出手表通信
                src_bd_addr = packet.bthci_acl.src_bd_addr
                dst_bd_addr = packet.bthci_acl.dst_bd_addr
                if (src_bd_addr != self.bd_addr and
                    dst_bd_addr != self.bd_addr):
                    continue

                payload = packet.btspp.data.binary_value

                # 将数据包拼接成完整的数据流
                if src_bd_addr == self.bd_addr:
                    # 手表 => 手机
                    self.w2p_buffer += payload
                else:
                    # 手机 => 手表
                    self.p2w_buffer += payload

            logger.info("重组完成! w2p_buffer: %d p2w_buffer: %d" % (len(self.w2p_buffer), len(self.p2w_buffer)))
            
            logger.info("开始分析w2p数据包...")

            while len(self.w2p_buffer) > 8:
                if struct.unpack("<H", self.w2p_buffer[:2])[0] == 0xA5A5:
                    pkt_type, seq, size, checksum = struct.unpack("<BBHH", self.w2p_buffer[2:8])
                    data = self.w2p_buffer[8:8+size]

                    if crc16(data) == checksum:
                        logger.debug("发现数据包 pkt_type: %d seq: %d size: %d checksum: %d" % (pkt_type, seq, size, checksum))
                        self.w2p_packets.append(MiPacket(pkt_type, seq, checksum, data))
                    else:
                        logger.debug("已跳过损坏数据包 %s != %s" % (hex(crc16(data)), hex(checksum)))
                        self.w2p_buffer = self.w2p_buffer[1:]
                        continue

                    self.w2p_buffer = self.w2p_buffer[8+size:]
                else:
                    logger.debug("已跳过无效字节")
                    self.w2p_buffer = self.w2p_buffer[1:]
            
            logger.info("分析完成! w2p_packets: %d" % len(self.w2p_packets))

            logger.info("开始分析p2w数据包...")

            while len(self.p2w_buffer) > 8:
                if struct.unpack("<H", self.p2w_buffer[:2])[0] == 0xA5A5:
                    pkt_type, seq, size, checksum = struct.unpack("<BBHH", self.p2w_buffer[2:8])
                    data = self.p2w_buffer[8:8+size]

                    if crc16(data) == checksum:
                        logger.debug("发现数据包 pkt_type: %d seq: %d size: %d checksum: %d" % (pkt_type, seq, size, checksum))
                        self.p2w_packets.append(MiPacket(pkt_type, seq, checksum, data))
                    else:
                        logger.debug("已跳过损坏数据包 %s != %s" % (hex(crc16(data)), hex(checksum)))
                        self.p2w_buffer = self.p2w_buffer[1:]
                        continue

                    self.p2w_buffer = self.p2w_buffer[8+size:]
                else:
                    logger.debug("已跳过无效字节")
                    self.p2w_buffer = self.p2w_buffer[1:]

            logger.info("分析完成! p2w_packets: %d" % len(self.p2w_packets))

            return True

        return False

class MassRipper:

    def __init__(self):
        self.files = {}

    def merge_file(self, file):

        md5 = file["md5"]
        total = file["total"]

        key = "%s-%d"  % (md5, total)

        if not key in self.files:
            logger.info("文件添加成功!")
            self.files[key] = file
        else:
            logger.info("文件存在已自动合并!")
            # 合并blocks
            for idx, data in file["blocks"].items():
                self.files[key]["blocks"][str(idx)] = data

    def load_pcap(self, file_name):

        logger.info("正在加载捕获日志... 文件名: %s" % file_name)

        try:
            pcap = MiCapture(file_name)
        except Exception as e:
            logger.error(e)
            logger.info("捕获日志加载失败!")

            if "tshark" in str(e).lower():
                raise WireSharkError()
            else:
                return False

        if pcap.succ:
            logger.info("捕获日志加载成功!")
        else:
            logger.info("捕获日志加载失败!")
            return False

        logger.info("正在筛选数据包...")

        cur_file = None

        for packet in pcap.p2w_packets:

            data = packet.data

            # 过滤杂包
            if len(data) < 32 and packet.pkt_type != PktType.Data.value:
                continue

            # PacketPayload
            channel, opcode = struct.unpack("BB", data[:2])

            if (channel == Channel.Data.value or channel == Channel.Activity.value) and opcode == OpCode.Plain.value:
            
                # 只有发送start后的第一个包包含header,最后一个包带有前面所有数据的crc
                total, cur = struct.unpack("<HH", data[2:6])

                if cur_file != None:

                    if total != cur_file["total"] or cur > cur_file["total"]:
                        logger.info("已跳过错误文件 文件md5: %s" % cur_file["md5"])
                        cur_file = None

                    logger.debug("发现目标数据包 %d/%d" % (cur, total))

                    if cur == total:
                        cur_file["blocks"][str(cur)] = data[6:len(data)-4]
                        cur_file["crc32"] = struct.unpack("<I", data[len(data)-4:])[0]
                        self.merge_file(cur_file)
                        logger.info("文件搜索完毕! crc32: %s" % hex(cur_file["crc32"]))
                        cur_file = None
                    else:
                        cur_file["blocks"][str(cur)] = data[6:]

                if start:

                    if cur_file != None:
                        self.merge_file(cur_file)
                        logger.info("文件搜索中断!")

                    cur_file = {}

                    header = data[2:28]
                    comp_data, data_type = struct.unpack("BB", header[4:6])
                    md5 = bytes(header[6:22]).hex()
                    size = struct.unpack("<I", header[22:26])[0]
                    
                    cur_file["header"] = header
                    cur_file["comp_data"] = comp_data
                    cur_file["data_type"] = data_type
                    cur_file["md5"] = md5
                    cur_file["size"] = size
                    cur_file["total"] = total
                    cur_file["blocks"] = {}
                    cur_file["crc32"] = 0

                    cur_file["blocks"][str(cur)] = data[28:]

                    logger.info("发现新文件 压缩类型: %d 数据类型: %s 文件md5: %s 文件大小: %d 起始传输区块: %d" % (comp_data ,MassDataType(data_type).name, md5, size, cur))
                
                start = False
            else:
                start = True
        
        return True

    def export_file(self, key):

        logger.info("正在导出文件 %s" % key)

        if key in self.files:

            buffer = b''
            md5 = hashlib.md5()

            file = self.files[key]

            for i in range(1, file["total"] + 1):

                if not str(i) in file["blocks"]:
                    logger.info("导出失败,文件分块不完整!")
                    return b''
                
                md5.update(file["blocks"][str(i)])
                buffer += file["blocks"][str(i)]
            
            if md5.hexdigest().lower() != file["md5"].lower():
                logger.info("导出失败,文件md5错误!")
                return b''
            
            logger.info("导出成功!")
            return buffer

        logger.info("导出失败,文件不存在!")

        return b''

    def get_file_list(self):
        return self.files.keys()

    def get_file(self, key):
        if key in self.files:
            return self.files[key]
        return None

    def dump_files(self):
        return msgpack.packb(self.files)
    
    def load_files(self, data):
        self.files = msgpack.unpackb(data)

