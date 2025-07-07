from aiogram.fsm.state import State, StatesGroup


class BaseInput(StatesGroup):
    """Базовый класс для групп состояний, содержащий общие состояния."""
    waiting_for_date = State()


class DrinkInput(BaseInput):
    """Группа состояний для ввода информации о выпивании алкоголя."""
    pass


class WeightInput(BaseInput):
    """Группа состояний для ввода информации о весе."""
    waiting_for_weight = State()
