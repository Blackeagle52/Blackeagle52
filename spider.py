import decimal

from collections import Counter
from unittest import TestCase


TICK_SPEED_RATIO = decimal.Decimal('0.07')
FULL_TM = decimal.Decimal('100')


class Toon:
    def __init__(self, *, name, speed):
        self.name = name
        self.speed = decimal.Decimal(speed)
        self.tm = decimal.Decimal('0')

    def __str__(self):
        return f"{self.name} ({self.speed} spd)"

    def __repr__(self):
        return str(self)

    def add_tick(self):
        self.tm += self.speed * TICK_SPEED_RATIO

    def has_turn(self):
        return self.tm > FULL_TM

    def reset_tm(self):
        self.tm = decimal.Decimal('0')


def get_turn_order(*, toons, max_turns=20):
    turns = 0
    order = []
    while turns < max_turns:
        for toon in toons:
            toon.add_tick()

        possible = [t for t in toons if t.has_turn()]
        if possible:
            next_toon = max(possible, key=lambda t: t.tm)
            order.append(next_toon)
            next_toon.reset_tm()
            turns += 1

    return order


class TurnOrderTestCase(TestCase):
    def setUp(self):
        # Speeds derived from default 4:3 UNM comp
        # https://www.deadwoodjedi.com/speed-tunes-4/1-Champ-after-AOE2
        # https://deadwoodjedi.info/cb/e4143c2c32d87ede848b04b7fe74fe6e457bbf03
        self.kreela = Toon(name='Kreela', speed=231)
        self.rhazin = Toon(name='Rhazin', speed=175)
        self.fb = Toon(name='FB', speed=174)
        self.brago = Toon(name='Brago', speed=173)
        self.skull = Toon(name='Skullcrusher', speed=172)
        self.cb = Toon(name='CB', speed=190)

        self.toons = [
            self.kreela, self.brago, self.fb, self.rhazin, self.skull, self.cb
        ]

    def test_tms_after_one_turn(self):
        _turns = get_turn_order(toons=self.toons, max_turns=1)
        self.assertEqual(_turns, [self.kreela])

        # TM of those who didn't have a turn
        self.assertEqual(round(self.cb.tm), 93, self.cb.tm)
        self.assertEqual(round(self.rhazin.tm), 86, self.rhazin.tm)
        self.assertEqual(round(self.fb.tm), 85, self.fb.tm)
        self.assertEqual(round(self.brago.tm), 85, self.brago.tm)
        self.assertEqual(round(self.skull.tm), 84, self.skull.tm)

        # TM of those who did have a turn, DWJ calculator shows tm > 100
        self.assertEqual(round(self.kreela.tm), 0, self.kreela.tm)

    def test_cb_turn_1(self):
        _turns = get_turn_order(toons=self.toons, max_turns=2)
        self.assertEqual(_turns, [self.kreela, self.cb])

        # TM of those who didn't have a turn
        self.assertEqual(round(self.rhazin.tm), 98, self.rhazin.tm)
        self.assertEqual(round(self.fb.tm), 97, self.fb.tm)
        self.assertEqual(round(self.brago.tm), 97, self.brago.tm)
        self.assertEqual(round(self.skull.tm), 96, self.skull.tm)

        # TM of those who did have a turn
        self.assertEqual(round(self.kreela.tm), 16, self.kreela.tm)
        self.assertEqual(round(self.cb.tm), 0, self.cb.tm)

    def test_cb_turn_2(self):
        _turns = get_turn_order(toons=self.toons, max_turns=8)
        self.assertEqual(_turns, [
            self.kreela,
            self.cb,
            self.rhazin,
            self.fb,
            self.brago,
            self.skull,
            self.kreela,
            self.cb,
        ])

        self.assertEqual(round(self.rhazin.tm), 86, self.rhazin.tm)
        self.assertEqual(round(self.fb.tm), 73, self.fb.tm)
        self.assertEqual(round(self.brago.tm), 61, self.brago.tm)
        self.assertEqual(round(self.skull.tm), 48, self.skull.tm)
        self.assertEqual(round(self.kreela.tm), 32, self.kreela.tm)
        self.assertEqual(round(self.cb.tm), 0, self.cb.tm)

    def test_cb_turn_6(self):
        _turns = get_turn_order(toons=self.toons, max_turns=33)
        # One toon must go twice before cb
        turns_after_aoe2 = _turns[len(_turns) - 8:]
        self.assertEqual(len(turns_after_aoe2), 8)
        self.assertEqual(turns_after_aoe2, [
            self.cb,
            self.kreela,
            self.rhazin,
            self.fb,
            self.brago,
            self.kreela,
            self.skull,
            self.cb,
        ], turns_after_aoe2)


class SpiderCalculator:
    def __init__(self, *, toons):
        for t in toons:
            t.reset_tm()

        self.toons = toons

        self.first_load = [
            Toon(name='\tSpiderling 1', speed=150),
            Toon(name='\tSpiderling 2', speed=150),
            Toon(name='\tSpiderling 3', speed=150),
            Toon(name='\tSpiderling 4', speed=150),
            Toon(name='\tSpiderling 5', speed=150),
            Toon(name='\tSpiderling 6', speed=150),
        ]
        self.second_load = [
            Toon(name='\tSpiderling 7', speed=150),
            Toon(name='\tSpiderling 8', speed=150),
        ]
        self.third_load = [
            Toon(name='\tSpiderling 9', speed=150),
            Toon(name='\tSpiderling 10', speed=150),
        ]

    def calculate_turn_order(self):
        turn_order = get_turn_order(
            toons=self.toons + self.first_load, max_turns=1,
        )
        turn_order.extend(
            get_turn_order(
                toons=self.toons + self.first_load + self.second_load,
                max_turns=1,
            )
        )
        turn_order.extend(
            get_turn_order(
                toons=self.toons + self.first_load + self.second_load + self.third_load,
                max_turns=25,
            )
        )
        return turn_order


def find_speed_tune():
    for speed_rg in range(125, 175):
        for speed_ck in range(200, 275):
            for speed_ig in range(speed_ck, 275):
                for speed_ch2 in range(speed_ig, 310):
                    for speed_ch1 in range(speed_ch2, 310):
                        toons = [
                            Toon(name='CH1', speed=speed_ch1),
                            Toon(name='CH2', speed=speed_ch2),
                            Toon(name='Ignatius', speed=speed_ig),
                            Toon(name='Crypt King', speed=speed_ck),
                            Toon(name='Renegade', speed=speed_rg),
                        ]

                        calculator = SpiderCalculator(toons=toons)
                        turn_order = calculator.calculate_turn_order()

                        counter = Counter(t.name for t in turn_order)
                        if (
                                counter['\tSpiderling 1'] == 2 and
                                counter['Crypt King'] == 3 and (
                                    '\tSpiderling 1' == turn_order[-1].name or (
                                        '\tSpiderling 1' == turn_order[-2].name and
                                        'Crypt King' != turn_order[-2].name
                                    )
                                )
                        ):
                            print("\n".join(str(t) for t in turn_order))
                            return

if __name__ == "__main__":
    # Don't uncomment, script takes a while to return a comp!
    # find_speed_tune()

    toons = [
        Toon(name='CH1', speed=300),
        Toon(name='CH2', speed=300),
        Toon(name='Ignatius', speed=255),
        Toon(name='Crypt King', speed=255),
        Toon(name='Renegade', speed=150),
    ]

    calculator = SpiderCalculator(toons=toons)
    print("\n".join(str(t) for t in calculator.calculate_turn_order()))

    # $ python spider.py 
    # CH1 (300 spd)
    # CH2 (300 spd)
    # Ignatius (255 spd)
    # Crypt King (255 spd)
    # CH1 (300 spd)
    # Renegade (150 spd)
    # CH2 (300 spd)
    # 	Spiderling 1 (150 spd)
    # 	Spiderling 2 (150 spd)
    # 	Spiderling 3 (150 spd)
    # 	Spiderling 4 (150 spd)
    # Ignatius (255 spd)
    # 	Spiderling 5 (150 spd)
    # 	Spiderling 6 (150 spd)
    # Crypt King (255 spd)
    # CH1 (300 spd)
    # CH2 (300 spd)
    # 	Spiderling 7 (150 spd)
    # 	Spiderling 8 (150 spd)
    # 	Spiderling 9 (150 spd)
    # 	Spiderling 10 (150 spd)
    # Ignatius (255 spd)
    # Renegade (150 spd)
    # CH1 (300 spd)
    # Crypt King (255 spd)
    # CH2 (300 spd)
    # 	Spiderling 1 (150 spd)    
