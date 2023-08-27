import grpc
from concurrent import futures
from collections import OrderedDict
import uhashring
import cache_service_pb2_grpc
from cache_service_pb2 import Key, CacheItem, NodeInfo, Response

class CacheServiceServicer(cache_service_pb2_grpc.CacheServiceServicer):
    def __init__(self, is_master=True, max_items=100):
        self.is_master = is_master
        self.nodes = []
        self.ring = uhashring.HashRing()
        self.cache = OrderedDict()  # Used only if is_master=False
        self.max_items = max_items  # Used for LRU

    def RegisterNode(self, request, context):
        if not self.is_master:
            return Response(success=False, message="Not a master node")
        
        node = f"{request.ip}:{request.port}"
        self.nodes.append(node)
        self.ring.add_node(node)

        return Response(success=True, message="Node registered successfully")

    def DeregisterNode(self, request, context):
        if not self.is_master:
            return Response(success=False, message="Not a master node")

        node = f"{request.ip}:{request.port}"
        if node in self.nodes:
            self.nodes.remove(node)
            self.ring.remove_node(node)

            return Response(success=True, message="Node deregistered successfully")
        return Response(success=False, message="Node not found")

    def Get(self, request, context):
        if self.is_master:
            node = self.ring.get_node(request.key)
            response = forward_request_to_slave(node, "Get", request)  # Cambio aquí de "Put" a "Get"
            return response
        else:
            value = self.cache.get(request.key, None)
            if value:
                # Move the accessed entry to the end (LRU update)
                self.cache.move_to_end(request.key)
                return CacheItem(key=request.key, value=value)
            else:
                return CacheItem(key=request.key, value="")

    def Put(self, request, context):
        if self.is_master:
            node = self.ring.get_node(request.key)
            print(f"Forwarding insertion of key '{request.key}' to node: {node}")  # Añadir este mensaje
            response = forward_request_to_slave(node, "Put", request)
            return response
        else:
            # If cache is full, remove the least recently used entry (LRU eviction)
            if len(self.cache) >= self.max_items:
                self.cache.popitem(last=False)
            self.cache[request.key] = request.value
            print(f"Inserted key '{request.key}' in local cache")  # Añadir este mensaje
            return Response(success=True, message="Inserted successfully")


    def Remove(self, request, context):
        if self.is_master:
            node = self.ring.get_node(request.key)
            response = forward_request_to_slave(node, "Remove", request)
            return response
        else:
            if request.key in self.cache:
                del self.cache[request.key]
                return Response(success=True, message="Removed successfully")
            return Response(success=False, message="Key not found")

def serve(is_master=True, port=50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    cache_service_pb2_grpc.add_CacheServiceServicer_to_server(CacheServiceServicer(is_master=is_master), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print (f"Server {is_master} started on port {port}")
    server.wait_for_termination()

def register_with_master(master_node, slave_ip, slave_port):
    print (f"Registering with master node {master_node}")
    with grpc.insecure_channel(master_node) as channel:
        stub = cache_service_pb2_grpc.CacheServiceStub(channel)
        response = stub.RegisterNode(NodeInfo(ip=slave_ip, port=slave_port))
        print(response.message)

def forward_request_to_slave(node, method, *args):
    with grpc.insecure_channel(node) as channel:
        stub = cache_service_pb2_grpc.CacheServiceStub(channel)
        if method == "Get":
            return stub.Get(*args)
        elif method == "Put":
            return stub.Put(*args)
        elif method == "Remove":
            return stub.Remove(*args)

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 3:
        print("Usage: python script_name.py [master/slave] [port]")
        exit(1)

    node_type, port = sys.argv[1], int(sys.argv[2])

    print (f"Starting {node_type} node on port {port}")

    if node_type == "master":
        serve(is_master=True, port=port)
    elif node_type == "slave":
        register_with_master("localhost:50051", "localhost", port)
        serve(is_master=False, port=port)
        print("Registering with master node")
    else:
        print("Unknown node type. Use 'master' or 'slave'.")
        exit(1)
