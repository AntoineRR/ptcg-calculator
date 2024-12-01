import json
from model import CardSetName, PullRates, Rarity


def main():
    with open("pull_rates.json", "r") as file:
        raw_pull_rates = json.load(file)
        pull_rates = PullRates.model_validate(raw_pull_rates)

    card_set = CardSetName.GENETIC_APEX
    n_booster = 100

    for rarity in Rarity:
        pull_rate = pull_rates.get_rates_for_card_set(card_set, rarity)

        print(
            f"Here are your chances of pulling cards of rarity {rarity.value} after opening one booster from {card_set.value}:"
        )
        for n, value in pull_rate.items():
            print(f"{round(value * 100.0, 2)}% to pull {n}")

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
