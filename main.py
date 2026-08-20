import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Crypto & Currency Converter", page_icon="💱", layout="centered")

st.title("💱 Конвертер Валют и Криптовалют")
st.write("Актуальный рыночный курс в реальном времени (Запросы через ваш браузер)")

with st.sidebar:
    st.header("⚙️ Настройки API")
    user_key = st.text_input("2f82046b08fef551287d936e", type="password")

# Встроенная база на экстренный случай
fallback_rates = {
    "USD": 1.0, "EUR": 0.93, "RUB": 94.2, "BYN": 3.28,
    "BTC": 0.000016, "ETH": 0.00042, "SOL": 0.0071, "XRP": 1.85
}

clean_key = "".join(user_key.split()) if user_key else ""

# JavaScript код, который выполнится прямо в твоем браузере на планшете
js_code = f"""
<script>
async function fetchAllRates() {{
    let rates = {{ "USD": 1.0 }};
    let debug = [];
    
    // 1. Получаем фиатные валюты напрямую в браузере
    let key = "{clean_key}";
    let fiatUrl = "https://er-api.com";
    if (key.length > 10) {{
        fiatUrl = "https://exchangerate-api.com" + key + "/latest/USD";
    }}
    
    try {{
        let res = await fetch(fiatUrl);
        let data = await res.json();
        let sourceRates = data.conversion_rates || data.rates;
        if (sourceRates) {{
            rates = {{...rates, ...sourceRates}};
            debug.push("✅ Фиат: курсы успешно загружены браузером.");
        }} else {{
            debug.push("⚠️ Фиат: некорректный ответ от API.");
        }}
    }} catch(e) {{
        debug.push("❌ Фиат: ошибка сети в браузере " + e.message);
    }}
    
    // 2. Получаем крипту через официальное зеркало Binance
    try {{
        let res = await fetch("https://binance.us");
        let data = await res.json();
        let cryptoSymbols = {{ "BTCUSDT": "BTC", "ETHUSDT": "ETH", "SOLUSDT": "SOL", "XRPUSDT": "XRP" }};
        
        if (Array.isArray(data)) {{
            data.forEach(item => {{
                if (cryptoSymbols[item.symbol]) {{
                    let price = parseFloat(item.price);
                    if (price > 0) {{
                        rates[cryptoSymbols[item.symbol]] = 1 / price;
                    }}
                }}
            }});
            debug.push("✅ Крипта: котировки успешно получены от Binance.");
        }}
    }} catch(e) {{
        debug.push("❌ Крипта: Binance заблокирован в браузере " + e.message);
    }}
    
    // Отправляем собранные данные обратно в Python-интерфейс Streamlit
    window.parent.postMessage({{type: 'streamlit:setComponentValue', value: JSON.stringify({{rates: rates, debug: debug}})}}, '*');
}}

// Запускаем сбор данных
setTimeout(fetchAllRates, 300);
</script>
"""

# Невидимый JS-компонент
receiver = components.html(js_code, height=0, width=0)

# Безопасный разбор данных в Python
rates = fallback_rates
debug_messages = ["⏳ Браузер запрашивает свежие курсы у бирж... Пожалуйста, подождите 1 секунду."]

if receiver and isinstance(receiver, str):
    try:
        parsed_data = json.loads(receiver)
        if isinstance(parsed_data, dict) and "rates" in parsed_data:
            rates = parsed_data["rates"]
            debug_messages = parsed_data["debug"]
    except Exception:
        pass

available_currencies = ["USD", "EUR", "RUB", "BYN", "BTC", "ETH", "SOL", "XRP"]

with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        from_curr = st.selectbox("Из какой валюты:", available_currencies, index=0)
    with col2:
        to_curr = st.selectbox("В какую валюту:", available_currencies, index=4)
        
    amount = st.number_input("Введите сумму:", min_value=0.0, value=100.0, step=1.0)
    
    if st.button("Конвертировать", type="primary", use_container_width=True):
        amount_in_usd = amount / rates.get(from_curr, fallback_rates[from_curr])
        result = amount_in_usd * rates.get(to_curr, fallback_rates[to_curr])
        st.success(f"### {amount:,.2f} {from_curr} = {result:.6f} {to_curr}")

with st.expander("🔍 Технический статус подключения к биржам"):
    for msg in debug_messages:
        st.write(msg)
