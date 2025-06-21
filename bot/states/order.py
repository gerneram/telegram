from aiogram.fsm.state import StatesGroup, State

class OrderFSM(StatesGroup):
    waiting_for_quantity = State()
    waiting_for_name = State()
    waiting_for_address = State()
    waiting_for_phone = State()
