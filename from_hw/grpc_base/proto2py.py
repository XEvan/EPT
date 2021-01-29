import os

# pip install grpcio #gRPC 的安装
# pip install protobuf  #ProtoBuf 相关的 python 依赖库
# pip install grpcio-tools   #python grpc 的 protobuf 编译工具
os.system('python -m grpc_tools.protoc -I. --python_out=./ --grpc_python_out=./ ./proto.proto')
