"""Содержит решение к ДЗ#01.1."""
import random
from math import isclose
from typing import Literal


class SomeModel:  # pragma: no cover
    """Класс, имитирующий какую-то модель, исключительно для обучения тестированию."""

    def predict(self, message: str) -> float:  # pragma: no cover
        """Имитирует сложносочинённые вычисления. Реализация не важна."""
        rng = random.Random(hash(message))
        return rng.random()


def predict_message_mood(
    message: str,
    model: SomeModel,
    bad_thresholds: float = 0.3,
    good_thresholds: float = 0.8,
) -> Literal["неуд"] | Literal["отл"] | Literal["норм"]:
    """Принимает на вход строку, экземпляр модели `SomeModel` и пороги хорошести.

    Returns
    -------
    - `"неуд"`, если предсказание модели меньше `bad_threshold`
    - `"отл"`, если предсказание модели больше `good_threshold`
    - `"норм"` в остальных случаях
    """
    verdict = model.predict(message)
    if verdict < bad_thresholds or isclose(verdict, bad_thresholds):
        return "неуд"
    if verdict > good_thresholds or isclose(verdict, good_thresholds):
        return "отл"
    return "норм"
