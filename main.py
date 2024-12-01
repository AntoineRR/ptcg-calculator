import json
from model import CardSetName, PullRates, Rarity


def main():
    with open("pull_rates.json", "r") as file:
        raw_pull_rates = json.load(file)
        pull_rates = PullRates.model_validate(raw_pull_rates)

    rarity = Rarity.TWO_STARS
    card_set = CardSetName.GENETIC_APEX
    n_booster = 137

    pull_rate = pull_rates.get_rate_for_card_set(card_set, rarity) * 100.0

    print(
        f"Here are your chances of pulling at least one card of rarity {rarity.value} after opening one booster from {card_set.value}:"
    )
    print(f"{round(pull_rate, 2)}%")
    print(
        f"On average, you need to open {round(100 / pull_rate, 2)} boosters to get one"
    )

    pull_rate_n = (
        pull_rates.get_rate_for_card_set_for_n_boosters(card_set, rarity, n_booster)
        * 100.0
    )
    print(
        f"Here are your chances of pulling at least one card of rarity {rarity.value} after opening {n_booster} boosters from {card_set.value}:"
    )
    print(f"{round(pull_rate_n, 2)}%")


if __name__ == "__main__":
    main()
