from .desligados_geral import DesligadosGeral
from .documentos import Documentos
from .gems import Gems
from .ibelong import IBelong
from .ot import OT
from .periodicos import Periodicos
from .quadro_geral import QuadroGeral
from .rp import RP
from .separation_forms import SeparationForms
from .speed import Speed
from .ult_mov_sal import UltMovSal
from .xcelerate import Xcelerate


AUTOMATIONS = {
    "Gems": Gems(),
    "Speed": Speed(),
    "Periódicos": Periodicos(),
    "XCelerate": Xcelerate(),
    "IBelong": IBelong(),
    "OT": OT(),
    "Rest Period": RP(),
    "Documentos": Documentos(),
    "Desligados Geral": DesligadosGeral(),
    "Separation Forms": SeparationForms(),
    "Ult Mov Sal": UltMovSal(),
    "Quadro Geral": QuadroGeral(),
}
