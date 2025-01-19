from qdrant_client import QdrantClient
from io import BytesIO
import streamlit as st
import base64

# Define qdrant collection name
collection_name = "dog_images"

# Setup state variable
if "selected_record" not in st.session_state:
    st.session_state.selected_record = None

# Function to set the selected record
def set_selected_record(new_record):
    st.session_state.selected_record = new_record

# Create qdrant client
@st.cache_resource
def get_client():
    return QdrantClient(
        url=st.secrets["qdrant_db_url"],
        api_key=st.secrets["qdrant_api_key"]
    )

# Function to show small sample of records when no record is selected
def get_initial_records():
    client = get_client()

    records, _ = client.scroll(
        collection_name=collection_name, 
        with_vectors=False,
        limit=12
    )

    return records

# Function to get similar images from the record
def get_similar_records():
    client = get_client()

    if st.session_state.selected_record is not None:
        return client.recommend(
            collection_name=collection_name,
            positive=[st.session_state.selected_record.id],
            limit=12
        )

    return records

# Function to convert image bytes to base64 string
def get_bytes_from_base64(base64_string):
    return base64.b64decode(base64_string)

# Get records
records = get_similar_records() if st.session_state.selected_record else get_initial_records()

# Show records
if st.session_state.selected_record:
    image_bytes = get_bytes_from_base64(st.session_state.selected_record.payload["base64"])
    st.header("Similar images:")
    st.image(image_bytes, use_column_width=True)
    st.divider()

# Setup columns
column = st.columns(3)

# Iterate over records and show images
for idx, record in enumerate(records):
    col_idx = idx % 3
    image_bytes = get_bytes_from_base64(record.payload["base64"])
    with column[col_idx]:
        st.image(image_bytes, use_container_width=True)
        st.button(
            label="Find similar images",
            key=record.id,
            on_click=set_selected_record,
            args=[record]
        )