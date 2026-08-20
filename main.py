import streamlit as st
import requests

# Настройка страницы сайта
st.set_page_config(page_title="Crypto & Currency Converter", page_icon="💱", layout="centered")

st.title("💱 Конвертер Валют и Криптовалют")
st.write("Актуальный рыночный курс в реальном времени")

@st.cache_data(ttl=600) # Кэшируем курсы на 10 минут, чтобы сайт работал быстрее
def get_rates():
    try:
        # Получаем фиатные валюты
        url = "https://er-api.com"
        rates = requests.get(url).json()["rates"]

        # Получаем криптовалюты
        crypto_url = "https://coingecko.com"
        crypto_data = requests.get(crypto_url).json()

        rates['BTC'] = 1 / crypto_data['bitcoin']['usd']
        rates['ETH'] = 1 / crypto_data['ethereum']['usd']
        rates['SOL'] = 1 / crypto_data['solana']['usd']
        rates['XRP'] = 1 / crypto_data['ripple']['usd']
        return rates, None
    except Exception as e:
        return None, str(e)

rates, error = get_rates()

if error:
    st.error(f"Ошибка загрузки курсов валют: {error}. Проверьте подключение к интернету.")
else:
    # Список доступных валют для выбора
    available_currencies = ["USD", "EUR", "RUB", "BYN", "BTC", "ETH", "SOL", "XRP"]
    
    # Создаем интерфейс в виде красивой карточки
    with st.container(border=True):
        col1, col2 = st.columns(2)
        
        with col1:
            from_curr = st.selectbox("Из какой валюты:", available_currencies, index=0)
        with col2:
            to_curr = st.selectbox("В какую валюту:", available_currencies, index=4) # по дефолту BTC
            
        amount = st.number_input("Введите сумму:", min_value=0.0, value=100.0, step=1.0)
        
        # Кнопка для конвертации
        if st.button("Конвертировать", type="primary", use_container_width=True):
            amount_in_usd = amount / rates[from_curr]
            result = amount_in_usd * rates[to_curr]
            
            # Красивый вывод результата
            st.success(f"### {amount:,.2f} {from_curr} = {result:.6f} {to_curr}")
            
    # Небольшая инфо-панель внизу страницы
    st.info("💡 Курсы обновляются автоматически. Используются официальные данные CoinGecko и ExchangeRate-API.")
