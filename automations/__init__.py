from .periodicos import Periodicos
from .speed import Speed
from .gems import Gems
from .xcelerate import Xcelerate
from .ibelong import IBelong

AUTOMATIONS = {
    "Periódicos": Periodicos(),
    "Speed": Speed(),
    "Gems": Gems(),
    "Xcelerate": Xcelerate(), 
    "IBelong": IBelong(),
}