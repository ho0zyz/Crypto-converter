import requests


def get_rates():
  url = "https://er-api.com"
  response = requests.get(url)
  data = response.json()
  rates = data["rates"]

  crypto_url = (
      "https://coingecko.com,"
      "solana,ripple&vs_currencies=usd"
  )
  crypto_response = requests.get(crypto_url)
  crypto_data = crypto_response.json()

  rates["BTC"] = 1 / crypto_data["bitcoin"]["usd"]
  rates["ETH"] = 1 / crypto_data["ethereum"]["usd"]
  rates["SOL"] = 1 / crypto_data["solana"]["usd"]
  rates["XRP"] = 1 / crypto_data["ripple"]["usd"]

  return rates


def convert():
  rates = get_rates()
  print("Доступные валюты: USD, EUR, RUB, BYN, BTC, ETH, SOL, XRP")

  from_curr = input("Из какой валюты (например, USD): ").upper()
  to_curr = input("В какую валюту (например, BTC): ").upper()
  amount = float(input("Введите сумму: "))

  if from_curr not in rates or to_curr not in rates:
    print("Ошибка: неверная валюта.")
    return

  amount_in_usd = amount / rates[from_curr]
  result = amount_in_usd * rates[to_curr]

  print(f"{amount} {from_curr} = {result:.6f} {to_curr}")


if __name__ == "__main__":
  convert()
