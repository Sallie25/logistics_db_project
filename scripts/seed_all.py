from scripts.seed_data import main as seed_fake_data
from scripts.seed_reference_data import seed_exchange_rates


def main():
    seed_exchange_rates()
    seed_fake_data()


if __name__ == "__main__":
    main()