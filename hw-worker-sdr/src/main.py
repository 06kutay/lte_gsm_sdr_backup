import os
import sys
import time
import logging
import grpc
from concurrent import futures

# Add root folder to sys.path so we can import proto and src correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config import settings, SdrType
from src.zmq_publisher import zmq_pub
from src.device_manager import device_manager
from src.grpc_server import serve_grpc

# Configure standard visual logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("main")

def register_to_backend():
    """
    Performs Service Discovery registration by making a RegisterMicroservice gRPC call
    to the main backend control server.
    """
    logger.info(f"Main Backend'e mikroservis kaydi yapiliyor ({settings.BACKEND_GRPC_ADDR})...")
    
    device_type = "SDR_LIMESDR" if settings.SDR_TYPE == SdrType.LIMESDR else "SDR_USRP"
    capabilities = ["SIB_PARSE", "NEIGHBOR_DISCOVERY", "CELL_SEARCH", "FREQ_SCAN", "GSM_SI_PARSE", "GSM_NEIGHBOR_DISCOVERY", "GSM_BAND_SCAN", "GSM_INTER_RAT_DISCOVERY"]
    control_endpoint = f"localhost:{settings.GRPC_PORT}"
    data_endpoint = f"tcp://localhost:{settings.ZMQ_PUB_PORT}"
    metadata = {
        "serial": settings.SDR_SERIAL,
        "role": settings.SDR_ROLE.value,
        "antenna": settings.antenna
    }

    # Resilient gRPC registration call
    try:
        # Check if the registration proto is available, if not, we emulate/mock the client registration channel.
        # This prevents absolute compilation errors when running worker in standalone mode.
        try:
            import proto.hw_common_pb2 as common_pb2
            import proto.hw_common_pb2_grpc as common_pb2_grpc
            
            channel = grpc.insecure_channel(settings.BACKEND_GRPC_ADDR)
            stub = common_pb2_grpc.BackendRegistrationServiceStub(channel)
            
            request = common_pb2.RegisterRequest(
                device_type=device_type,
                capabilities=capabilities,
                control_endpoint=control_endpoint,
                data_endpoint=data_endpoint,
                metadata=metadata
            )
            response = stub.RegisterMicroservice(request, timeout=3)
            logger.info(f"✅ Backend mikroservis kaydi basarili! Response: {response.message}")
        except ImportError:
            # Fallback/emulated mode if hw-common-proto is not compiled in local development
            logger.warning("hw_common_pb2 stubs bulunamadi. Kayit istegi simüle ediliyor.")
            logger.info(
                f"[SIMÜLE KAYIT] Type: {device_type}, Caps: {capabilities}, "
                f"Ctrl: {control_endpoint}, Data: {data_endpoint}, Meta: {metadata}"
            )
    except Exception as e:
        logger.warning(f"⚠️ Backend kaydi basarisiz (Backend cevrimdisi olabilir): {e}")

def main():
    logger.info("======================================================================")
    logger.info("         📡 HW-WORKER-SDR GRPC MIKROSERVISI CALISTIRILIYOR 📡")
    logger.info("======================================================================")
    logger.info(f"SDR Tipi            : {settings.SDR_TYPE.value.upper()}")
    logger.info(f"SDR Seri No         : {settings.SDR_SERIAL or 'TANIMSIZ'}")
    logger.info(f"SDR Rolü            : {settings.SDR_ROLE.value.upper()}")
    logger.info(f"SDR Anten Portu     : {settings.antenna}")
    logger.info(f"gRPC Servis Portu   : {settings.GRPC_PORT}")
    logger.info(f"ZMQ Event Portu     : {settings.ZMQ_PUB_PORT}")
    logger.info("======================================================================")

    # 1. Start ZMQ Publisher
    zmq_pub.start()

    # 2. Start gRPC Server
    grpc_server = serve_grpc()

    # 3. Start Device Manager (will trigger backend registration once device is active)
    device_manager.start(on_serving_callback=register_to_backend)

    # 4. Keep alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Kapatma sinyali alindi (SIGINT)...")
    finally:
        logger.info("Servisler kapatiliyor...")
        device_manager.stop()
        grpc_server.stop(grace=1)
        zmq_pub.close()
        logger.info("Mikroservis basariyla kapatildi. Hosçakalin.")

if __name__ == "__main__":
    main()
