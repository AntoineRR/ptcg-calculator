import json
from model import CardSetName, PullRates, Rarity


def main():
    with open("pull_rates.json", "r") as file:
        raw_pull_rates = json.load(file)
        pull_rates = PullRates.model_validate(raw_pull_rates)

    card_set = CardSetName.GENETIC_APEX
    n_booster = 137

    for rarity in Rarity:
        print(
            f"Here are your chances of pulling cards of rarity {rarity.value} after opening {n_booster} boosters from {card_set.value}:"
        )
        for m_card in range(40):
            pull_rate_n = (
                pull_rates.get_rate_for_m_card_set_for_n_boosters(
                    card_set, rarity, n_booster, m_card
                )
                * 100.0
            )
            if pull_rate_n > 0.1:
                print(f"{round(pull_rate_n, 2)}% to pull {m_card}")


if __name__ == "__main__":
    main()
