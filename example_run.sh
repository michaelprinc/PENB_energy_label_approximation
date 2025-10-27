#!/bin/bash
# Příklad použití energetického štítku

echo "======================================"
echo "Příklad 1: Starý byt s plynovým kotlem"
echo "======================================"
python energeticky_stitek.py \
  --area 75 \
  --ceiling-height 2.6 \
  --heat-source gas-boiler \
  --efficiency 0.9 \
  --daily-consumption 25 \
  --indoor-temp 21 \
  --location Prague \
  --people 2 \
  --output priklad1_plynovykotel.txt

echo ""
echo "======================================"
echo "Příklad 2: Moderní byt s tepelným čerpadlem"
echo "======================================"
python energeticky_stitek.py \
  --area 65 \
  --ceiling-height 2.5 \
  --heat-source heat-pump \
  --efficiency 3.5 \
  --daily-consumption 12 \
  --indoor-temp 20 \
  --location Brno \
  --people 2 \
  --output priklad2_tepelnecerpadlo.txt

echo ""
echo "======================================"
echo "Příklad 3: Malý byt s elektrickým topením"
echo "======================================"
python energeticky_stitek.py \
  --area 45 \
  --ceiling-height 2.8 \
  --heat-source electric \
  --efficiency 0.99 \
  --daily-consumption 18 \
  --indoor-temp 22 \
  --location Ostrava \
  --people 1 \
  --output priklad3_elektricke.txt

echo ""
echo "Všechny příklady byly úspěšně zpracovány!"
