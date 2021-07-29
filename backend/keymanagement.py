import secrets

def generate_seed(length=16):
    with open("backend/db/words.txt", "r") as f:
        words = f.read().strip().split("\n")

    out = []
    for i in range(length):
        out.append(secrets.choice(words))

    return out


if __name__ == "__main__":
    print(generate_seed())