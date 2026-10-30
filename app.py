import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Hermes Agent", page_icon="🤖")
st.title("مساعدي الشخصي - Hermes Agent")
st.write("تطبيق شات سحابي يعمل 24/7 بدون الحاجة لإنعاش اللابتوب.")

api_key = st.secrets.get("OPENROUTER_API_KEY")

if not api_key:
    st.error("الرجاء إضافة OPENROUTER_API_KEY في إعدادات الأسرار (Secrets) على Streamlit.")
    st.stop()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("اكتب رسالتك هنا..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            stream = client.chat.completions.create(
                model="nvidia/nemotron-3.5-lightning:free",
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                stream=True,
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"حدث خطأ: {e}")
