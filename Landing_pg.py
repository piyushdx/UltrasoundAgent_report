import streamlit as st
from config import config, environment, ip_config

IP = ip_config[environment]
response_port = config['BotApplication']['Frontend']  # response API
url = f'http://{IP}:{response_port}/'

#Title
st.markdown(
    """
    <h1 style='text-align: center;'>Ultrasound Report Assistant</h1>
    """,
    unsafe_allow_html=True,)

st.markdown(
    """
    <h6 style='text-align:left;'>Welcome to DX Labs, where cutting-edge technology meets human potential! 
    Revolutionize your medical practice with the Ultrasound Report Assistant: an indispensable tool that empowers doctors to work much more efficiently and effortlessly, save valuable time, and gain crystal-clear insights with this cutting-edge solution tailored to enhance your diagnostic accuracy.</h6>
    """, unsafe_allow_html=True)

st.markdown("---")

st.markdown(
    """ 
    <h3 style='text-align:left;'>Ultrasound report Assistant</h3>
    """, unsafe_allow_html=True)
st.write(f"[View Demo]({url}UltraBot)")
st.markdown("---")