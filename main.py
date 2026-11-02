import argparse
from Orquest.pipeline.website import build

def main():
    parser = argparse.ArgumentParser(description="Orquestrador de sites com DeepSeek")
    parser.add_argument("brief", help="Descrição do site que você quer")
    args = parser.parse_args()

    build(args.brief)

if __name__ == "__main__":
    main()