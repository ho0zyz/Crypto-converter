import streamlit as st
import requests

st.set_page_config(page_title="Crypto & Currency Converter", page_icon="💱", layout="centered")

st.title("💱 Конвертер Валют и Криптовалют")
st.write("Актуальный рыночный курс в реальном времени")

# Выносим поле ввода ключа прямо в красивый интерфейс сайта (для удобства)
with st.sidebar:
    st.header("⚙️ Настройки API")
    user_key = st.text_input("2f82046b08fef551287d936e", type="password", help="Ключ от сайта exchangerate-api.com")

@st.cache_data(ttl=600)
def get_rates(api_key):
    # Локальная база (на самый крайний случай)
    rates = {
        "USD": 1.0, "EUR": 0.92, "RUB": 91.5, "BYN": 3.26,
        "BTC": 0.000015, "ETH": 0.00038, "SOL": 0.0068, "XRP": 1.72
    }
    debug_info = []

    # 1. Пробуем получить фиатные валюты
    if api_key and len(api_key).strip() > 5:
        # Вариант А: Через ваш личный API-ключ
        try:
            res = requests.get(f"https://exchangerate-api.com{api_key.strip()}/latest/USD", timeout=5)
            if res.status_code == 200:
                rates.update(res.json().get("conversion_rates", {}))
                debug_info.append("✅ Фиатные курсы: успешно обновлены через ваш API-ключ.")
            else:
                debug_info.append(f"❌ Ошибка личного ключа: сервер вернул статус {res.status_code}.")
        except Exception as e:
            debug_info.append(f"❌ Ошибка подключения к личному API: {str(e)}")
    else:
        # Вариант Б: Открытый бесплатный шлюз (без ключа), если поле пустое
        try:
            res = requests.get("https://er-api.com", timeout=5)
            if res.status_code == 200:
                rates.update(res.json().get("rates", {}))
                debug_info.append("✅ Фиатные курсы: обновлены через публичный резервный шлюз.")
            else:
                debug_info.append("❌ Публичный шлюз фиата недоступен.")
        except Exception as e:
            debug_info.append(f"❌ Сбой публичного шлюза фиата: {str(e)}")

    # 2. Пробуем получить криптовалюты через CoinCap
    try:
        crypto_res = requests.get("https://coincap.io", timeout=5)
        if crypto_res.status_code == 200:
            data = crypto_res.json().get("data", [])
            for asset in data:
                symbol = asset.get("symbol")
                price_usd = float(asset.get("priceUsd", 0))
                if price_usd > 0:
                    rates[symbol] = 1 / price_usd
            debug_info.append("✅ Криптовалюты: актуальные котировки успешно получены.")
        else:
            debug_info.append("❌ Сервер CoinCap перегружен. Используются базовые крипто-коэффициенты.")
    except Exception as e:
        debug_info.append(f"❌ Сбой сети при запросе крипты: {str(e)}")

    return rates, debug_info

# Загружаем данные на основе ввода
rates, debug_messages = get_rates(user_key)

available_currencies = ["USD", "EUR", "RUB", "BYN", "BTC", "ETH", "SOL", "XRP"]

# Основной интерфейс приложения
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

# Вывод технического отчета для отслеживания проблемы
with st.expander("🔍 Технический статус подключения к биржам"):
    for msg in debug_messages:
        st.write(msg)
