import streamlit as st
import pandas as pd
import numpy as np
import requests as reqs

st.title("People")

resp = reqs.get("http://localhost:8080/people?size=1000").json()

df = pd.DataFrame(resp["_embedded"]["people"])

if len(df)>=1:          # empty df에서 오류 발생함.
    df["href"] = df["_links"].apply(lambda x:x["person"]["href"])


    df = df[["firstName", "lastName", "href"]]
    df["etc"]=[False]*len(df)


edited_df = st.data_editor(
    df,
    disabled=["href"],
    column_config={
        "href": st.column_config.LinkColumn("href"),
    }
)


left, middle, right = st.columns(3)
############# Create ###################################
@st.dialog("New Person")
def add():
    import requests as reqs

    first = st.text_input("firstName",  placeholder="Peter")
    last = st.text_input("lastName",  placeholder="Parker")


    if st.button("Add Person"):
        resp = reqs.post("http://localhost:8080/people", json={"firstName": first, "lastName": last}, headers = {'Content-Type': 'application/json'})
        if 200<=resp.status_code<400:
            # st.write("성공적으로 저장되었습니다.")
            st.rerun()
        else:
            st.warn("오류가 있습니다", resp.text)


if left.button("add Person"):
    add()
############# Create End ###############################

############# Update ###################################
if "df_value" not in st.session_state:
    st.session_state.df_value = df


def boolTransform(row1, row2):
    for c in row1[row1.columns.difference(["etc"])]:
        if row1[c].item()!=row2[c].item():
            return False
    return True

def update(edited_df):
    for i in range(len(edited_df)):
        if (boolTransform(edited_df.iloc[[i]],df.iloc[[i]]))==False:
            first = edited_df.iloc[[i]]["firstName"].item()
            last = edited_df.iloc[[i]]["lastName"].item()
            reqs.put(edited_df.iloc[i]["href"], json={"firstName": first, "lastName": last}, headers = {'Content-Type': 'application/json'})
            st.rerun()


if edited_df is not None and not edited_df.equals(st.session_state["df_value"]):
    # This will only run if
    # 1. Some widget has been changed (including the dataframe editor), triggering a
    # script rerun, and
    # 2. The new dataframe value is different from the old value
    update(edited_df)
    st.session_state["df_value"] = edited_df
############# Update End ###############################


if right.button("Delete"):
    for i in range(len(edited_df["etc"])):
        if edited_df["etc"].iloc[i]:
            reqs.delete(edited_df.iloc[i]["href"])
    st.rerun()
