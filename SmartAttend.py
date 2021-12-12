import streamlit as st
import os
import pandas as pd
import datetime

def paginator(label, items, items_per_page=10, on_sidebar=True):
    # Figure out where to display the paginator
    if on_sidebar:
        location = st.sidebar.empty()
    else:
        location = st.empty()

    # Display a pagination selectbox in the specified location.
    items = list(items)
    n_pages = len(items)
    n_pages = (len(items) - 1) // items_per_page + 1
    page_format_func = lambda i: "Page %s" % str(i + 1)
    page_number = location.selectbox(label, range(n_pages), format_func=page_format_func)

    # Iterate over the items in the page to let the user display them.
    min_index = page_number * items_per_page
    max_index = min_index + items_per_page
    import itertools
    return itertools.islice(enumerate(items), min_index, max_index)


# import h
df = pd.read_csv(r"/Users/joey/Desktop/hackathon/venv/smartAttendance/attendance.csv", encoding='latin1')

st.title("Smart Attendance System")
st.caption('By Team Radioactive')

# both checkin check out
result = st.button('Run Camera')
if result:
    os.system('python /Users/joey/Desktop/hackathon/venv/smartAttendance/main.py')

d = st.date_input(
    "Select Date",
    datetime.date(2020,12,11))
# st.write('The dates available', d)
print(d)

result1 = st.button('Sheet')

if result1:
    st.write('The dates available are', d)
    st.dataframe(df)

result2 = st.button("Display images")
if result2:
    imgs = [x for x in os.listdir("/Users/joey/Desktop/hackathon/venv/smartAttendance") if x.endswith(".png")]
    image_iterator = paginator("Select page", imgs, on_sidebar=False)
    indices_on_page, images_on_page = map(list, zip(*image_iterator))
    st.image(images_on_page, width=200, caption=indices_on_page)
