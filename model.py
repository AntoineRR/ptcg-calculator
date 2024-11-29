from enum import Enum
from pydantic import BaseModel

class Rarity(Enum):
    ONE = "ONE"
    TWO = "TWO"
    THREE = "THREE"
    FOUR = "FOUR"
    ONE_STAR = "ONE_STAR"
    TWO_STARS = "TWO_STARS"
    THREE_STARS = "THREE_STARS"
    CROWN = "CROWN"

class RarityRate(BaseModel):
    rarity: Rarity
    rate: float = 0.0

class Pack(BaseModel):
    name: str
    god_pack_rate: float
    rates: list[list[RarityRate]]
    god_rates: list[list[RarityRate]]

    def get_rarity_rate(self, rarity_rates: list[RarityRate], rarity: Rarity):
        try:
            return next(elt.rate for elt in rarity_rates if elt.rarity == rarity) * 0.01
        except StopIteration:
            return 0.0

    def get_booster_rate(self, rates: list[list[RarityRate]], rarity: Rarity):
        win_rate = 0.0
        previous_win_rate = 0.0
        for card_rates in rates:
            current_win_rate = self.get_rarity_rate(card_rates, rarity)
            win_rate += (1.0 - previous_win_rate) * current_win_rate 
            previous_win_rate = win_rate

        return win_rate * 100.0


    def get_rate(self, rarity: Rarity):
        god_rate = self.god_pack_rate * 0.01 * self.get_booster_rate(self.god_rates, rarity)
        normal_rate = (1.0 - self.god_pack_rate * 0.01) * self.get_booster_rate(self.rates, rarity)
        return god_rate + normal_rate


class CardSet(BaseModel):
    name: str
    packs: list[Pack]

    def get_pack(self, pack_name: str):
        return next(elt for elt in self.packs if elt.name == pack_name)

    def get_rate(self, pack_name: str, rarity: Rarity):
        pack = self.get_pack(pack_name)
        return pack.get_rate(rarity)



class PullRates(BaseModel):
    card_sets: list[CardSet]

    def get_card_set(self, card_set_name: str):
        return next(elt for elt in self.card_sets if elt.name == card_set_name)

    def get_rate(self, card_set_name: str, pack_name: str, rarity: Rarity):
        card_set = self.get_card_set(card_set_name)
        return card_set.get_rate(pack_name, rarity)