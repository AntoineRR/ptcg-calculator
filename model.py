from enum import Enum
import itertools
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

    def get_booster_rate(
        self, rates: list[list[RarityRate]], rarity: Rarity
    ) -> dict[int, float]:
        """
        Return the probabilities of pulling cards of the specified rarity
        """
        rarity_rates = [
            self.get_rarity_rate(rates[x], rarity) for x in range(len(rates))
        ]
        result = {}

        zero_pull_rate = 1.0
        for rate in rarity_rates:
            zero_pull_rate *= 1.0 - rate  # Only fails
        result[0] = zero_pull_rate

        for n in range(1, 5):
            n_pull_rate = 0.0
            combinations = itertools.combinations([0, 1, 2, 3, 4], n)
            for comb in combinations:
                p = 1.0
                for x in range(len(rarity_rates)):
                    if x in comb:
                        p *= rarity_rates[x]  # n wins
                    else:
                        p *= 1.0 - rarity_rates[x]  # and len(rarity_rates) - n fails
                n_pull_rate += p
            result[n] = n_pull_rate

        five_pull_rate = 1.0
        for rate in rarity_rates:
            five_pull_rate *= rate  # Only wins
        result[5] = five_pull_rate

        return result

    def get_rate(self, rarity: Rarity) -> dict[int, float]:
        """
        Return the probabilities of pulling cards of the specified rarity from one booster
        """
        god_rates = self.get_booster_rate(self.god_rates, rarity)
        normal_rates = self.get_booster_rate(self.rates, rarity)
        return {
            x: normal_rates[x] * (1.0 - self.god_pack_rate * 0.01)
            + god_rates[x] * self.god_pack_rate * 0.01
            for x in normal_rates
        }


class CardSet(BaseModel):
    name: CardSetName
    packs: list[Pack]

    def get_pack(self, pack_name: PackName) -> Pack:
        return next(elt for elt in self.packs if elt.name == pack_name)

    def get_rate_for_pack(
        self, pack_name: PackName, rarity: Rarity
    ) -> dict[int, float]:
        return self.get_pack(pack_name).get_rate(rarity)

    def get_rates(self, rarity: Rarity) -> dict[int, float]:
        """
        Return the mean probabilities of getting cards of the specified rarity for this set
        """
        rates = {}
        for pack in self.packs:
            for x, value in self.get_rate_for_pack(pack.name, rarity).items():
                rates[x] = rates.setdefault(x, 0.0) + value
        for x in rates:
            rates[x] /= len(self.packs)
        return rates


class PullRates(BaseModel):
    card_sets: list[CardSet]

    def get_card_set(self, card_set_name: CardSetName) -> CardSet:
        return next(elt for elt in self.card_sets if elt.name == card_set_name)

    def get_rate_for_pack(
        self, card_set_name: CardSetName, pack_name: PackName, rarity: Rarity
    ) -> dict[int, float]:
        return self.get_card_set(card_set_name).get_rate_for_pack(pack_name, rarity)

    def get_rates_for_card_set(
        self, card_set_name: CardSetName, rarity: Rarity
    ) -> dict[int, float]:
        return self.get_card_set(card_set_name).get_rates(rarity)

    def get_rate_for_card_set_for_n_boosters(
        self, card_set_name: CardSetName, rarity: Rarity, n_booster: int
    ) -> float:
        """
        Probability of getting at least one card of specified rarity from n boosters
        """
        ps = self.get_rates_for_card_set(card_set_name, rarity)
        p = 0.0
        for i in range(1, 5):  # Assuming there are 5 cards in the booster
            p += ps[i]
        return 1.0 - pow(1.0 - p, n_booster)
