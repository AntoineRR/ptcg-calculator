from enum import Enum
from pydantic import BaseModel, Field


class Rarity(Enum):
    ONE = "ONE"
    TWO = "TWO"
    THREE = "THREE"
    FOUR = "FOUR"
    ONE_STAR = "ONE_STAR"
    TWO_STARS = "TWO_STARS"
    THREE_STARS = "THREE_STARS"
    CROWN = "CROWN"


class PackName(Enum):
    pass


class GeneticApexPackName(PackName):
    CHARIZARD = "CHARIZARD"
    MEWTWO = "MEWTWO"
    PIKACHU = "PIKACHU"


class CardSetName(Enum):
    GENETIC_APEX = "GENETIC_APEX"


class RarityRate(BaseModel):
    rarity: Rarity
    rate: float = Field(ge=0.0, le=100.0, default=0.0)


class Pack(BaseModel):
    name: GeneticApexPackName
    god_pack_rate: float
    rates: list[list[RarityRate]]
    god_rates: list[list[RarityRate]]

    def get_rarity_rate(self, rarity_rates: list[RarityRate], rarity: Rarity) -> float:
        try:
            return next(elt.rate for elt in rarity_rates if elt.rarity == rarity) * 0.01
        except StopIteration:
            return 0.0

    def get_booster_rate(self, rates: list[list[RarityRate]], rarity: Rarity) -> float:
        """
        Return the probability of pulling at least one card of the specified rarity
        """
        zero_pull_rate = 1.0
        for card_rates in rates:
            zero_pull_rate *= 1.0 - self.get_rarity_rate(card_rates, rarity)
        return 1.0 - zero_pull_rate

    def get_rate(self, rarity: Rarity) -> float:
        """
        Return the probability of pulling at least one card of the specified rarity from one booster
        """
        god_rate = (
            self.god_pack_rate * 0.01 * self.get_booster_rate(self.god_rates, rarity)
        )
        normal_rate = (1.0 - self.god_pack_rate * 0.01) * self.get_booster_rate(
            self.rates, rarity
        )
        return god_rate + normal_rate


class CardSet(BaseModel):
    name: CardSetName
    packs: list[Pack]

    def get_pack(self, pack_name: PackName) -> Pack:
        return next(elt for elt in self.packs if elt.name == pack_name)

    def get_rate_for_pack(self, pack_name: PackName, rarity: Rarity) -> float:
        return self.get_pack(pack_name).get_rate(rarity)

    def get_rate(self, rarity: Rarity) -> float:
        rates = 0.0
        for pack in self.packs:
            rates += self.get_rate_for_pack(pack.name, rarity)
        return rates / len(self.packs)


class PullRates(BaseModel):
    card_sets: list[CardSet]

    def get_card_set(self, card_set_name: CardSetName) -> CardSet:
        return next(elt for elt in self.card_sets if elt.name == card_set_name)

    def get_rate_for_pack(
        self, card_set_name: CardSetName, pack_name: PackName, rarity: Rarity
    ) -> float:
        return self.get_card_set(card_set_name).get_rate_for_pack(pack_name, rarity)

    def get_rate_for_card_set(
        self, card_set_name: CardSetName, rarity: Rarity
    ) -> float:
        return self.get_card_set(card_set_name).get_rate(rarity)

    def get_rate_for_card_set_for_n_boosters(
        self, card_set_name: CardSetName, rarity: Rarity, n_booster: int
    ) -> float:
        """
        Probability of getting at least one card of specified rarity from n boosters
        """
        p = self.get_rate_for_card_set(card_set_name, rarity)
        # We now have a Bernoulli law to apply
        return 1.0 - pow(1.0 - p, n_booster)
