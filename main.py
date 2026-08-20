import streamlit as st
import requests

st.set_page_config(page_title="Crypto & Currency Converter", page_icon="💱", layout="centered")

st.title("💱 Конвертер Валют и Криптовалют")
st.write("Актуальный рыночный курс в реальном времени")

# Локальная база (надежный встроенный бэкап)
rates = {
    "USD": 1.0, "EUR": 0.93, "RUB": 94.2, "BYN": 3.28,
    "BTC": 0.000016, "ETH": 0.00042, "SOL": 0.0071, "XRP": 1.85
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Твой жестко зашитый личный ключ
api_key = "2f82046b08fef551287d936e"

# 1. ЗАПРОС ФИАТНЫХ ВАЛЮТ
fiat_status = "⚠️ Сбой сети. Активен встроенный бэкап курсов."
try:
    fiat_url = f"https://exchangerate-api.com{api_key}/latest/USD"
    res = requests.get(fiat_url, headers=headers, timeout=5)
    if res.status_code == 200 and "conversion_rates" in res.json():
        rates.update(res.json()["conversion_rates"])
        fiat_status = "🟢 ОТЛИЧНО: Живые курсы фиата успешно получены по вашему API-ключу!"
    else:
        # Резервный публичный запрос
        res_pub = requests.get("https://er-api.com", headers=headers, timeout=5)
        if res_pub.status_code == 200 and "rates" in res_pub.json():
            rates.update(res_pub.json()["rates"])
            fiat_status = "🟡 РЕЗЕРВ: Использован открытый шлюз (личный ключ отклонен)."
except Exception as e:
    fiat_status = f"🔴 ОШИБКА ПОДКЛЮЧЕНИЯ: {str(e)[:60]}. Включен встроенный бэкап."

# 2. ЗАПРОС КРИПТОВАЛЮТЫ ИЗ БИРЖИ KUCOIN
crypto_status = "⚠️ Сбой сети. Активен встроенный бэкап крипты."
crypto_mapping = {"BTC-USDT": "BTC", "ETH-USDT": "ETH", "SOL-USDT": "SOL", "XRP-USDT": "XRP"}
try:
    crypto_res = requests.get("https://api.kucoin.com/api/v1/market/allTickers", headers=headers, timeout=5)
    if crypto_res.status_code == 200:
        raw_data = crypto_res.json().get("data", {}).get("ticker", [])
        for item in raw_data:
            pair = item.get("symbol")
            if pair in crypto_mapping:
                price_usd = float(item.get("last", 0))
                if price_usd > 0:
                    rates[crypto_mapping[pair]] = 1 / price_usd
        crypto_status = "🟢 ОТЛИЧНО: Живые котировки крипты успешно получены от KuCoin!"
    else:
        crypto_status = f"🟡 РЕЗЕРВ: Биржа вернула код {crypto_res.status_code}. Включен встроенный бэкап."
except Exception as e:
    crypto_status = f"🔴 ОШИБКА КРИПТЫ: {str(e)[:60]}. Включен встроенный бэкап."


# ИНТЕРФЕЙС КОНВЕРТЕРА
available_currencies = ["USD", "EUR", "RUB", "BYN", "BTC", "ETH", "SOL", "XRP"]

with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        from_curr = st.selectbox("Из какой валюты:", available_currencies, index=0)
    with col2:
        to_curr = st.selectbox("В какую валюту:", available_currencies, index=4)
        
    amount = st.number_input("Введите сумму:", min_value=0.0, value=100.0, step=1.0)
    
    if st.button("Конвертировать", type="primary", use_container_width=True):
        amount_in_usd = amount / rates.get(from_curr, 1.0)
        result = amount_in_usd * rates.get(to_curr, 1.0)
        st.success(f"### {amount:,.2f} {from_curr} = {result:.6f} {to_curr}")

# Панель статуса без скрытых логических условий
st.subheader("🔍 Статус соединения с биржами:")
st.info(fiat_status)
st.info(crypto_status)
