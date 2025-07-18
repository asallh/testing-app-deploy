import streamlit as st
import time

# Set page config
st.set_page_config(page_title="🚀 My Awesome App", page_icon="🔥", layout="centered")

# Title and subtitle
st.title("🚀 Welcome to My Awesome Streamlit App!")
st.subheader("Your journey into interactive web apps starts here 🎉")
st.write("This is branch:")
st.write("Dev")

# Cool intro text
st.markdown(
    """
    This app is built with [Streamlit](https://streamlit.io) — a fast way to build custom web apps for machine learning and data science.

    👉 Use the button below to get started!
    """
)

# Button to trigger action
if st.button("✨ Launch Magic!"):
    st.success("Magic launched! Loading something cool...")

    progress_bar = st.progress(0)
    for i in range(1, 101):
        time.sleep(0.01)
        progress_bar.progress(i)
    
    st.snow()
    st.markdown("### 🎯 You're all set! Let's build something amazing.")

# Footer
st.markdown("---")
st.caption("Made with ❤️ using Streamlit")
