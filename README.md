
# Steam Game Market Analysis Dashboard

An interactive data visualization dashboard exploring trends among the most popular games on Steam. This project investigates how characteristics such as price, genre, ratings, developer output, and player activity relate to game popularity using live SteamSpy data.

Built with **Python**, **Pandas**, **Altair**, and **Streamlit**.

---

## Project Overview

The goal of this project is to better understand what makes some Steam games significantly more successful than others by analyzing approximately the top 1,000 Steam games available today.

The dashboard allows users to:

- Filter games by price, rating, genre tags, and free-to-play status
- Explore relationships between game price, ownership estimates, ratings, and concurrent players
- Compare the popularity of different game genres
- Analyze developer performance based on the number of released games and estimated ownership
- Interactively brush and select points to examine subsets of games across multiple linked visualizations

---

## Dashboard Features

### Interactive Filters

- Price range
- Rating range
- Free-to-play filter
- Multi-select game tags

### Visualizations

- **Estimated Owners vs Price**

  - Logarithmic owner scale
  - Bubble size represents concurrent players
- **Estimated Owners vs Rating**

  - Explore how review scores relate to popularity
- **Top 15 Game Tags**

  - Compare ownership across major genres
  - Linked interaction with scatterplots
- **Developer Analysis**

  - Compare developers by:
    - Total estimated owners
    - Median estimated owners
    - Number of released games
    - Median game rating

---

## Data Source

Game information was collected using the SteamSpy API.

SteamSpy provides estimated ownership ranges rather than exact sales figures. These ownership ranges were converted into midpoint estimates during preprocessing for visualization purposes.

The data includes approximately the **top 1,000 Steam games**, meaning the analysis focuses on already successful titles and should not be interpreted as representing every game available on Steam.

---

## Data Cleaning

Several preprocessing steps were performed before visualization, including:

- Converting SteamSpy ownership ranges into midpoint estimates
- Converting prices from cents to dollars
- Creating game rating percentages from positive and negative reviews
- Extracting primary game tags
- Expanding tag dictionaries for multi-tag filtering
- Creating derived metrics used throughout the dashboard

---

## Repository Structure

```
Main/
│
├── Data_Analysis/
│   ├── Dashboard/
│       ├── streamlit_eda.py
│   └── First_EDA_old_data/
│       ├── eda_steam.ipynb
│       ├── steam.csv
│
├── Dataset/
│   ├── Data/Download/
│       ├── app_list.csv
│       ├── steam_spy_data.csv
│       ├── steamspy_index.txt
│   ├── Data_Collection/
│       ├── get_data.py
├── EDA/
│   ├── Exploratory analysis notebooks
│   └── Feature engineering experiments
│
├── Presentations/
│   ├── Proposal_presentaion.pdf
│   ├── EDA_presentation.pdf
│   └── Dashboard_presentation.pdf
│
├── requirements.txt
└── README.md
```

---

## Technologies Used

- Python
- Pandas
- Altair
- Streamlit
- SteamSpy API

---

## Running the Dashboard

Clone the repository:

```bash
git clone https://github.com/yourusername/yourrepository.git
cd Steam_EDA
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the dashboard:

```bash
streamlit run app.py
```

---

## Project Highlights

Some notable findings include:

- Free-to-play games account for many of the largest player bases.
- Higher game prices are not strongly associated with larger ownership.
- Extremely poorly rated games rarely achieve high ownership.
- Survival, Open World, and Free-to-Play games consistently appear among the most popular titles.
- Developers with more releases do not necessarily produce more successful games, although large publishers tend to dominate total ownership.

---

## Acknowledgements

Steam data was collected using the SteamSpy API.

Much of the original API collection workflow was adapted from:

Nik Davis
https://nik-davis.github.io/posts/2019/steam-data-collection/

This project extends that workflow with additional preprocessing, feature engineering, exploratory analysis, and an interactive Streamlit dashboard.

---

## Author

Sage Rudder

Boston College — AA Applied Data Science — BS Computer Science
