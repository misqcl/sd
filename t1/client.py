import grpc
import cache_service_pb2
import cache_service_pb2_grpc

class CacheClient:
    def __init__(self, host="localhost", port=50051):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = cache_service_pb2_grpc.CacheServiceStub(self.channel)

    def put(self, key, value):
        response = self.stub.Put(cache_service_pb2.CacheItem(key=key, value=value))
        print(response.message)

    def get(self, key):
        response = self.stub.Get(cache_service_pb2.Key(key=key))
        if response.value:  # Comprobar si hay un valor, en lugar de 'exists'
            return response.value
        else:
            print("Key not found.")
            return None

    def remove(self, key):
        response = self.stub.Remove(cache_service_pb2.Key(key=key))
        print(response.message)


if __name__ == '__main__':
    client = CacheClient()

    while True:
        print("\nChoose an operation:")
        print("1. Put")
        print("2. Get")
        print("3. Remove")
        print("4. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            key = input("Enter key: ")
            value = input("Enter value: ")
            client.put(key, value)
        elif choice == "2":
            key = input("Enter key: ")
            value = client.get(key)
            if value is not None:
                print(f"Value: {value}")
        elif choice == "3":
            key = input("Enter key: ")
            client.remove(key)
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")
