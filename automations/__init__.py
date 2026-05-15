# =========================================================
# automations/__init__.py
# =========================================================

from automations.gems import Gems
from automations.speed import Speed
from automations.periodicos import Periodicos
from automations.xcelerate import Xcelerate
from automations.ibelong import IBelong

from automations.ot import OT
from automations.rp import RP
from automations.documentos import Documentos
from automations.desligados_geral import DesligadosGeral
from automations.separation_forms import SeparationForms
from automations.ult_mov_sal import UltMovSal
from automations.quadro_geral import QuadroGeral


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