import altair as alt
import pandas as pd 
import streamlit as st
import ast 


st.set_page_config(
    page_title="Steam Game Analysis",
    layout="wide")

st.write(
    "**Steam Data Analysis**")

st.write(
    "The goal for this analysis is to better understand what makes some Steam games so much more popular than others by looking at trends and patterns within the top ~1000 steam games today."
)

#replacing old data with new data
#steam = pd.read_csv('steam.csv')
#../../Dataset/data/download/steamspy_data.csv

new_data_path = "steamspy_data.csv"
steam = pd.read_csv(new_data_path)
pd.set_option("display.max_columns", None)


#data cleaning for raw steamspy data

#owners clean
owners = (
    steam["owners"]
    .str.replace(",", "", regex=False)
    .str.split(" .. ", expand=True)
)

owners = owners.apply(pd.to_numeric)

steam["owners_min"] = owners[0]
steam["owners_max"] = owners[1]

steam["owners_avg"] = owners.mean(axis=1).astype(int)

steam["owners"] = (
    steam["owners_avg"]
)

#price clean

steam["initialprice"] = (steam["initialprice"] / 100).round(2)


steam["price"] = (steam["price"] / 100).round(2)

#Tags clean

steam["main_tag"] = (
    steam["tags"]
    .str.split(":")
    .str[0]
    .str.replace("{'", "", regex=False)
    .str.replace("'", "", regex=False)
)

#creating rating score column pos / pos+neg

steam["rating"] = (
    steam["positive"] / (steam["positive"] + steam["negative"])
).round(2)



#makes a new datafraame tracking all different tags and scores for each game



# Convert each tags value from a string into a real dictionary
steam["tags_dict"] = steam["tags"].apply(
    lambda value: ast.literal_eval(value)
    if pd.notna(value) and value != "{}"
    else {}
)

# Turn each game's dictionary into separate tag rows
steam_tags = (
    steam[
        [
            "appid",
            "name",
            "owners_avg",
            "price",
            "positive",
            "negative",
            "tags_dict"
        ]
    ]
    .explode("tags_dict")
    .rename(columns={"tags_dict": "tag"})
)

# Pull the score for each tag from the original dictionary
steam_tags["tag_score"] = steam_tags.apply(
    lambda row: steam.loc[row.name, "tags_dict"].get(row["tag"]),
    axis=1
)

# Remove games with no tags
steam_tags = steam_tags.dropna(subset=["tag"]).reset_index(drop=True)

#SIDEBAR


st.sidebar.header("Apply Filters")


st.sidebar.caption(
    "Selecting multiple tags only shows games containing every selected tag."
)

selected_tags = st.sidebar.multiselect("Select Game Tags", options= steam_tags["tag"].unique())

free_games = st.sidebar.checkbox("Free games")

if free_games:
    pass
else:
    price_range = st.sidebar.slider( "Select desired price range",
        int(steam["price"].min()),
        int(steam["price"].max()),
        (int(steam["price"].min()), int(steam["price"].max()))
)

rating_range = st.sidebar.slider( "Select desired rating)",
    float(steam["rating"].min()),
    float(steam["rating"].max()),
    (float(steam["rating"].min()), float(steam["rating"].max()))
)





filtered_df = steam.copy()

#tags
if selected_tags:
    matching_apps = (
        steam_tags[steam_tags["tag"].isin(selected_tags)]
        .groupby("appid")["tag"]
        .nunique()
    )

    matching_appids = matching_apps[
        matching_apps == len(selected_tags)
    ].index

    filtered_df = filtered_df[
        filtered_df["appid"].isin(matching_appids)
    ]

if filtered_df.empty:
    st.warning("No games match the selected parameters.")
    st.stop()
#price range
if free_games:
    pass
else:
    filtered_df = filtered_df[filtered_df["price"].between(*price_range)]

#rating

filtered_df = filtered_df[filtered_df["rating"].between(*rating_range)]

# free

if free_games:
    filtered_df = filtered_df[filtered_df["price"] == 0 ]


#METRICS

games = len(filtered_df)
med_rating = round(filtered_df["rating"].median(),2)
med_price = round(filtered_df["price"].median(), 2)
med_owners = int(filtered_df["owners"].median())


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Games", games)

with col2:
    st.metric("Median Owners", med_owners)

with col3:
    st.metric("Median Price", f"${med_price}")

with col4:
    st.metric("Median Rating", med_rating)

#making charts


#selections
tag_click = alt.selection_point(fields=["main_tag"], on="click", empty=False, name = "tag_click")
brush = alt.selection_interval()


#owners over price chart (owner_price)

owners_price = alt.Chart(filtered_df).mark_circle(size = 75).encode(
    x = alt.X("price:Q"),
   
    y = alt.Y(
    "owners_avg:Q",
    scale=alt.Scale(type="log"),
    title="Estimated Owners"
),
color = alt.when(tag_click).then(alt.value("orange")) 
    .when(brush).then(alt.value("Steelblue")) 
    .otherwise(alt.value("grey")),
    opacity = alt.condition(tag_click, alt.value(1), alt.value(.15)),

  
    size = alt.Size("ccu:Q", title = "Online players(ccu)", scale= alt.Scale(domain=(0, 45000), range=(40, 250))),


    tooltip=["name:N", "main_tag:N", "publisher:N",
        alt.Tooltip("owners_avg:Q",
                    title="Estimated Owners",
                    format=","),
        alt.Tooltip("price:Q",
                    title="Price",
                    format="$.2f"),
        alt.Tooltip("ccu:Q",
                    title="Concurrent Players",
                    format=","),
        alt.Tooltip("rating:Q",
                    title="Rating",
                    format=".2%")
    ]
).add_params(brush).properties(title ="Game Owners Over Price")#ratings over owners chart (rating_owners)

owners_rating = alt.Chart(filtered_df).mark_point(size = 75).encode(
    y = alt.Y("rating:Q"),
   
    x = alt.X(
    "owners_avg:Q",
    scale=alt.Scale(type="log"),
    title="Estimated Owners"
),
    color = alt.when(tag_click).then(alt.value("orange")) 
        .when(brush).then(alt.value("Steelblue")) 
        .otherwise(alt.value("grey")),
    opacity = alt.when(brush).then(alt.value(1)).otherwise(alt.value(.10)),

    size = alt.Size("ccu:Q", title = "Online players(ccu)", scale= alt.Scale(domain=(0, 45000), range=(40, 250))),

    tooltip= ["name:N", "main_tag:N", "publisher:N",
        alt.Tooltip("owners_avg:Q",
                    title="Estimated Owners",
                    format=","),
        alt.Tooltip("price:Q",
                    title="Price",
                    format="$.2f"),
        alt.Tooltip("ccu:Q",
                    title="Concurrent Players",
                    format=","),
        alt.Tooltip("rating:Q",
                    title="Rating",
                    format=".2%")
    ]).add_params(brush).properties(title = "Game Rating Over Price")


#top tags chart (top_tags)

top_15_tags = (
    filtered_df.groupby("main_tag")["owners"]
    .sum()
    .nlargest(15)
    .index.tolist()
)

background = (alt.Chart(filtered_df).transform_filter(alt.FieldOneOfPredicate(
    field="main_tag",
    oneOf=top_15_tags
    )).mark_bar(color="lightgray").encode(
        x=alt.X("main_tag:N", sort=top_15_tags, title="Main Tag"),
   
        y=alt.Y("sum(owners):Q", title="Total Owners"),
        tooltip=[
            alt.Tooltip("main_tag:N", title="Main Tag"),
            alt.Tooltip("sum(owners):Q", title="Overall Total Owners", format=",.0f"),
            alt.Tooltip("median(owners):Q", title="Overall Median Owners", format=",.0f")
        ]
    )
)

foreground = (alt.Chart(filtered_df)
    .transform_filter(brush)
    .transform_filter(
        alt.FieldOneOfPredicate(field="main_tag",oneOf=top_15_tags)
        ) 
    .mark_bar()
    .encode(
        x=alt.X("main_tag:N", sort=top_15_tags, title="Main Tag"),
        y=alt.Y("sum(owners):Q", title="Total Owners"),
        color = alt.when(tag_click).then(alt.value("orange")).otherwise(alt.value("steelblue")),
        
        tooltip=[
            alt.Tooltip("main_tag:N", title="Main Tag"),
            alt.Tooltip(
                "sum(owners):Q",
                title="Selected Total Owners",
                format=",.0f"
            ),
            alt.Tooltip(
                "median(owners):Q",
                title="Selected Median Owners",
                format=",.0f"
            ),
            alt.Tooltip(
                "count():Q",
                title="Selected Games"
            )
        ]
    )
).add_params(tag_click)

#layer

top_tags = (
    background + foreground
).properties(
    title="Top 15 Main Tags by Owners",
    width=850,
    height=300
)

selection = 0

if selection == 1:
    y = "Total Owners"
    y_var = 'sum_owners:Q'
    y2 = "Median Owners"
    y2_var = 'med_owners:Q'
else:
    y = "Median Owners"
    y_var = 'med_owners:Q'
    y2 = "Total Owners"
    y2_var = 'sum_owners:Q'

#owners over developers dev (owners_dev)

pub_grouped = filtered_df.groupby('developer').agg(
    med_owners=('owners','median'),
    med_ratings=('rating','median'),
    sum_owners = ('owners','sum'),
    count = ("appid", 'count')
).reset_index()
print(pub_grouped.head())

owners_dev0 = alt.Chart(pub_grouped).mark_circle(size = 100).encode(
    x = alt.X('count:Q', title='Number of Games'),
    y = alt.Y(y_var, title= y, scale= alt.Scale(type="log")),
    size = alt.Size("med_ratings:Q", title = "Ratings", scale= alt.Scale(domain=(0.55, 0.99), range=(40, 250))),

    tooltip= ["developer:N","count:Q",
        alt.Tooltip(y_var,
                    title= y),
        alt.Tooltip(y2_var,
                    title=y2),
        alt.Tooltip("med_ratings:Q",
                    title="Median Rating",
                    format=".2%")]
).properties(
    title = f'{y} vs Number of Games by Developer'
)
#selection = st.radio("Choose y variable", ["Total Owners", "Median Owners"])
selection = 1

if selection == 1:
    y = "Total Owners"
    y_var = 'sum_owners:Q'
    y2 = "Median Owners"
    y2_var = 'med_ownes:Q'
else:
    y = "Median Owners"
    y_var = 'med_owners:Q'
    y2 = "Total Owners"
    y2_var = 'sum_owners:Q'

#owners over developers dev (owners_dev)

pub_grouped = filtered_df.groupby('developer').agg(
    med_owners=('owners','median'),
    med_ratings=('rating','median'),
    sum_owners = ('owners','sum'),
    count = ("appid", 'count')
).reset_index()
print(pub_grouped.head())

owners_dev1 = alt.Chart(pub_grouped).mark_circle(size = 100).encode(
    x = alt.X('count:Q', title='Number of Games'),
    y = alt.Y(y_var, title= y, scale= alt.Scale(type="log")),
    size = alt.Size("med_ratings:Q", title = "Ratings", scale= alt.Scale(domain=(0.55, 0.99), range=(40, 250))),

    tooltip= ["developer:N","count:Q",
        alt.Tooltip(y_var,
                    title= y),
        alt.Tooltip(y2_var,
                    title=y2),
        alt.Tooltip("med_ratings:Q",
                    title="Median Rating",
                    format=".2%")]
).properties(
    title = f'{y} vs Number of Games by Developer'
)



#Placing charts

linked_charts = (
    (owners_price | owners_rating)
    & top_tags
)

st.altair_chart(
    linked_charts,
  #  use_container_width=True
)

selection = st.radio(
    "Choose developer metric",
    ["Total Owners", "Median Owners"],
    horizontal=True
)

developer_chart = (
    owners_dev1
    if selection == "Total Owners"
    else owners_dev0
)

st.altair_chart(
    developer_chart,
    use_container_width=True)