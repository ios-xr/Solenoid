from grpc.beta import implementations
import ems_grpc_pb2

class CiscoGRPCClient(object):
    def __init__(self, server, port, timeout, user, password):
        self._server = server
        self._port = port
        self._channel = implementations.insecure_channel(self._server, self._port)
        self._stub = ems_grpc_pb2.beta_create_gRPCConfigOper_stub(self._channel)
        self._timeout = int(timeout)
        self._metadata = [('username', user), ('password', password)]

    def getconfig(self, path):
        message = ems_grpc_pb2.ConfigGetArgs(yangpathjson=path)
        responses = self._stub.GetConfig(message,self._timeout, metadata = self._metadata)
        objects = ''
        for response in responses:
            objects += response.yangjson
        return objects

    def mergeconfig (self, yangjson):
        message = ems_grpc_pb2.ConfigArgs(yangjson= yangjson)
        response = self._stub.MergeConfig(message, self._timeout, metadata = self._metadata)
        return response

    def deleteconfig (self, yangjson):
        message = ems_grpc_pb2.ConfigArgs(yangjson= yangjson)
        response = self._stub.DeleteConfig(message, self._timeout, metadata = self._metadata)
        return response

    def replaceconfig (self, yangjson):
        message = ems_grpc_pb2.ConfigArgs(yangjson= yangjson)
        response= self._stub.ReplaceConfig(message, self._timeout, metadata = self._metadata)
        return response

