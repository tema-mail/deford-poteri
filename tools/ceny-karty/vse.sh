#!/bin/zsh
# Цены по городам с Яндекс Карт по очереди, один поток. Остановка (капча, 429, нет сети) – ждём 45 мин и продолжаем
# с места остановки, до 4 попыток на город. Лог – data/karty/vse.log. Запуск: nohup caffeinate -i zsh tools/ceny-karty/vse.sh spb ekb ... &
cd "$(dirname "$0")/../.."
LOG=data/karty/vse.log
for kod in "$@"; do
  for popytka in 1 2 3 4; do
    echo "$(date '+%d.%m %H:%M') $kod: попытка $popytka" >> $LOG
    python3 tools/ceny-karty/sbor.py $kod harvest >> data/karty/$kod-harvest.out 2>&1
    kodv=$?
    if [ $kodv -eq 0 ]; then echo "$(date '+%d.%m %H:%M') $kod: готово" >> $LOG; break; fi
    echo "$(date '+%d.%m %H:%M') $kod: остановка (код $kodv), жду 45 мин" >> $LOG
    sleep 2700
  done
done
echo "$(date '+%d.%m %H:%M') всё" >> $LOG
