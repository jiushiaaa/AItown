import json
import socket
import os
import sys
import logging

# 检查是否在WebGL环境下运行
WEB_MODE = os.environ.get('WEB_MODE', 'False').lower() == 'true'

# 如果是Web模式，导入WebSocket适配器
if WEB_MODE:
    try:
        from websocket_adapter import websocketclient as websocket_client
        logging.info("已启用WebSocket模式")
    except ImportError as e:
        logging.error(f"无法导入WebSocket适配器: {e}")
        # 设置为False以使用标准Socket
        WEB_MODE = False

class socketclient():
    def __init__(self,host,port):
        self.host = host
        self.port = port
        
        # 如果是Web模式，使用WebSocket适配器
        if WEB_MODE:
            try:
                print(f"以WebSocket模式初始化服务器 {host}:{port}")
                from websocket_adapter import websocketclient
                self.client = websocketclient(host, port)
                self.is_websocket = True
                print(f"WebSocket服务器启动在 {host}:{port}")
                return
            except Exception as e:
                print(f"WebSocket初始化失败，将回退到标准Socket: {e}")
                # 出错时回退到标准Socket
                self.is_websocket = False
        else:
            self.is_websocket = False
        
        # 标准Socket模式
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow reusing the address to avoid WinError 10048
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(1)
        print("Server listening on port", self.port)
        self.conn,self.addr = self.server.accept()
        print(f"Connected by {self.addr}")

    def send(self,data):
        # 如果是Web模式，使用WebSocket适配器
        if WEB_MODE:
            try:
                return self.client.send(data)
            except Exception as e:
                print(f"WebSocket发送失败: {e}")
                return False
        
        # 标准Socket模式
        try:
            data = json.dumps(data,ensure_ascii=False,indent=4)
            self.conn.sendall(data.encode())
            return True
        except (BrokenPipeError, ConnectionResetError) as e:
            print(f"连接已断开: {e}")
            self.close()
            return False
        except Exception as e:
            print(f"发送数据时出错: {e}")
            return False

    def recv(self):
        # 如果是Web模式，使用WebSocket适配器
        if WEB_MODE:
            try:
                return self.client.receive()
            except Exception as e:
                print(f"WebSocket接收失败: {e}")
                return False
        
        # 标准Socket模式
        try:
            data = self.conn.recv(1024)
            if not data:
                print("Received No return")
                return False
            if data:
                data = json.loads(data)
                print(data)
                return data
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"解析接收数据时出错: {e}")
            return False
        except (ConnectionResetError, BrokenPipeError) as e:
            print(f"连接已断开: {e}")
            self.close()
            return False
        except Exception as e:
            print(f"接收数据时出错: {e}")
            return False
    
    def close(self):
        """关闭socket连接"""
        # 如果是Web模式，使用WebSocket适配器
        if WEB_MODE:
            try:
                if hasattr(self, 'client'):
                    self.client.close()
                print("WebSocket connection closed")
                return
            except Exception as e:
                print(f"关闭WebSocket连接时出错: {e}")
                return
        
        # 标准Socket模式
        try:
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()
            if hasattr(self, 'server') and self.server:
                self.server.close()
            print("Socket connection closed")
        except Exception as e:
            print(f"关闭socket连接时出错: {e}")



