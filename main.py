import json
from model import PullRates, Rarity


def main():
    with open("pull_rates.json", "r") as file:
        raw_pull_rates = json.load(file)
        pull_rates = PullRates.model_validate(raw_pull_rates)
    
    print(pull_rates.get_rate("genetic_apex", "charizard", Rarity.CROWN))


if __name__ == "__main__":
    main()
