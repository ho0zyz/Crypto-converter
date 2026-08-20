import streamlit as st
import requests

st.set_page_config(page_title="Crypto & Currency Converter", page_icon="💱", layout="centered")

st.title("💱 Конвертер Валют и Криптовалют")
st.write("Актуальный рыночный курс в реальном времени")

with st.sidebar:
    st.header("⚙️ Настройки API")
    user_key = st.text_input("2f82046b08fef551287d936e", type="password", help="Ваш личный ключ от exchangerate-api.com")

@st.cache_data(ttl=300)
def get_rates(api_key):
    # Локальная база (надежный бэкап)
    rates = {
        "USD": 1.0, "EUR": 0.93, "RUB": 94.2, "BYN": 3.28,
        "BTC": 0.000016, "ETH": 0.00042, "SOL": 0.0071, "XRP": 1.85
    }
    debug_info = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    clean_key = api_key.strip() if api_key else ""

    # 1. Запрос мировых валют (Фиат)
    if clean_key and len(clean_key) > 5:
        try:
            res = requests.get(f"https://exchangerate-api.com{clean_key}/latest/USD", headers=headers, timeout=5)
            if res.status_code == 200:
                rates.update(res.json().get("conversion_rates", {}))
                debug_info.append("✅ Фиатные курсы: успешно обновлены через ваш личный API-ключ.")
            else:
                debug_info.append(f"❌ Ошибка личного ключа. Сервер вернул код {res.status_code}.")
        except Exception as e:
            debug_info.append(f"❌ Ошибка подключения к личному API: {str(e)}")
    else:
        debug_info.append("ℹ️ Фиатные курсы: используется стабильный локальный шлюз (вставьте ключ слева для реалтайма).")

    # 2. Запрос криптовалют через абсолютно стабильный CoinCap (взамен упавшего CoinGecko)
    try:
        crypto_res = requests.get("https://coincap.io", headers=headers, timeout=5)
        if crypto_res.status_code == 200:
            data = crypto_res.json().get("data", [])
            for asset in data:
                symbol = asset.get("symbol") # BTC, ETH, SOL, XRP
                price_usd = float(asset.get("priceUsd", 0))
                if price_usd > 0:
                    rates[symbol] = 1 / price_usd
            debug_info.append("✅ Криптовалюты: живые биржевые котировки успешно получены от CoinCap.")
        else:
            debug_info.append(f"⚠️ Сервер CoinCap временно занят (Код {crypto_res.status_code}). Включен резерв.")
    except Exception as e:
        debug_info.append(f"❌ Сбой сети при запросе крипты: {str(e)}")

    return rates, debug_info

rates, debug_messages = get_rates(user_key)
available_currencies = ["USD", "EUR", "RUB", "BYN", "BTC", "ETH", "SOL", "XRP"]

with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        from_curr = st.selectbox("Из какой валюты:", available_currencies, index=0)
    with col2:
        to_curr = st.selectbox("В какую валюту:", available_currencies, index=4)
        
    amount = st.number_input("Введите сумму:", min_value=0.0, value=100.0, step=1.0)
    
    if st.button("Конвертировать", type="primary", use_container_width=True):
        amount_in_usd = amount / rates[from_curr]
        result = amount_in_usd * rates[to_curr]
        st.success(f"### {amount:,.2f} {from_curr} = {result:.6f} {to_curr}")

with st.expander("🔍 Технический статус подключения к биржам"):
    for msg in debug_messages:
        st.write(msg)
