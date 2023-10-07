# Проба 1 (баллы 4)

## Done

* внутренние подкаталоги затрудняют проверку, лучше без них
    <https://github.com/relicks/deep_python_23b_aalitvinov/commit/d6d245ea115ff309fa0f50b8326ba50b426168e1>
* +проверки, что передается в predict модели в тестах (см. `test_predict_message_mood.test_call_predict`)
    <https://github.com/relicks/deep_python_23b_aalitvinov/commit/57aea7ca1f1a1790478a01feb0caacd4fd407c3b>
* +краевые и околокраевые случаи порогов для предикта (см. `test_predict_message_mood.test_borders`)
    <https://github.com/relicks/deep_python_23b_aalitvinov/commit/3ecb8f6cd91412e526588dd04beaee5f791959ec>
* +тесты с изменением порогов предиктора (см. `test_predict_message_mood.test_threshold_tweaks`)
    <https://github.com/relicks/deep_python_23b_aalitvinov/commit/dc7b15c64de87a063b45a970977743f989873431>

* +тесты генератора: <https://github.com/relicks/deep_python_23b_aalitvinov/commit/af49d628a26393de04544604b01ffb9d2aa03e71>
  * несколько совпадений,
    * см. `test_read_generator.TestGrepIter.test_several_words`
  * проверка совпадения с учетом регистронезависимости,
    * см. `test_read_generator.TestGrepIter.test_word_case`
  * совпадение нескольких фильтров в одной строке,
    * см. `test_read_generator.TestGrepIter.test_several_matches`
  * слово фильтр целиком совпадает со строкой в файле
    * см. `test_read_generator.TestGrepIter.test_match_whole_line`

## TODO

...
