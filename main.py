from Alert.Alerta import Alerta
from mainOrchestrator import MainOrchestrator
def job():
    mc = MainOrchestrator()
    mc.Extract()
    al = Alerta()
    al.send_imoveis()



job()
