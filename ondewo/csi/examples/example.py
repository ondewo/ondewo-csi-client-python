from ondewo_csi.csi_server import CsiServer

if __name__ == "__main__":
    service = CsiServer()
    service.serve()
