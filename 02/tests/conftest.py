# pylint: disable=no-member
from random import Random

import orjson
import pytest
from faker import Faker
from faker.providers import BaseProvider

SEED = 99


class RandomCaseWordsProvider(BaseProvider):
    def random_case_words(self, n_words: int = 3) -> list[str]:
        words_list: list[str] = self.generator.words(nb=n_words)
        rng = Random(SEED)
        for i, word in enumerate(words_list):
            if rng.choice((True, False)):
                words_list[i] = word.capitalize()
        return words_list


class JsonStringProvider(BaseProvider):
    def json_dict(
        self,
        n_rows: int = 3,
        n_words: int = 3,
        join_sep: str = " ",
    ):
        self.generator.add_provider(RandomCaseWordsProvider)
        rng = Random(SEED)
        return dict(
            zip(
                self.generator.random_case_words(n_rows),
                (
                    join_sep.join(
                        self.generator.random_case_words(rng.choice(range(1, n_words)))
                    )
                    for _ in range(n_rows)
                ),
                strict=True,
            ),
        )


@pytest.fixture(scope="session", autouse=True)
def faker_session_locale():
    return ["cs_CZ"]


@pytest.fixture(scope="session", autouse=True)
def faker_seed():
    return SEED


@pytest.fixture(scope="session")
def json_str_alpha() -> str:
    return orjson.dumps(
        {
            "decade": "Name land six Do task box",
            "Value": "medical Article plant price Try more",
            "almost": "decision particular data into over",
            "apply": "hard",
            "provide": "million Hard",
            "Trade": "Agree dinner try",
            "why": "Product",
        }
    ).decode("utf-8")


@pytest.fixture(scope="session")
def json_str_beta() -> str:
    return orjson.dumps(
        {
            "Головной!": "изредка палка заплакать точно Холодно лиловый Угодный Табак",
            "Инте_рнет": "порядок Спешить мрачно 6.2 Спалить задержать Мучительно Жить",
            "монет@": "головка Стакан Подземный миф",
            "34876командование": "Светило_Некоторый даль головной dinner",
            "Изменение": "За Научить Видимо ремень Порт Художественный Волк Команда",
            "Ведьg": "Редактор",
        }
    ).decode("utf-8")


@pytest.fixture()
def json_str_giant(faker: Faker) -> str:
    faker.add_provider(JsonStringProvider)
    return orjson.dumps(faker.json_dict(1_000, 1_000)).decode("utf-8")
