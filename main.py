import json
from model import PullRates, Rarity


def main():
    with open("pull_rates.json", "r") as file:
        raw_pull_rates = json.load(file)
        pull_rates = PullRates.model_validate(raw_pull_rates)
    
    rarity = Rarity.ONE_STAR
    card_set = "genetic_apex"
    pack = "mewtwo"

    pull_rate = pull_rates.get_rate(card_set, pack, rarity)

    print(f"Here are your chances of pulling a card of rarity {rarity.value} after opening one {pack} booster from {card_set}:")
    print(f"{round(pull_rate, 2)}%")
    print(f"On average, you need to open {round(100 / pull_rate, 2)} boosters to get one")


if __name__ == "__main__":
    main()
