from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

team_colors = {"Ravens": (26, 25, 95), "Bengals": (251, 79, 20), "Browns": (49, 29, 0),
               "Steelers": (255, 182, 18), "Bills": (0, 51, 141), "Dolphins": (0, 142, 151),
               "Patriots": (0, 34, 68), "Jets": (18, 87, 64), "Texans": (3, 32, 47), 
               "Colts": (0, 44, 95), "Jaguars": (16, 24, 32), "Titans": (12, 35, 64),
               "Broncos": (251, 79, 20), "Chiefs": (227, 24, 55), "Raiders": (0, 0, 0), 
               "Chargers": (0, 128, 198), "Lions": (0, 118, 182), "Packers": (24, 48, 40),
               "Vikings": (79, 38, 131), "Cowboys": (0, 53, 148), "Giants": (1, 35, 82),
               "Eagles": (0, 76, 84), "Commanders": (90, 20, 20), "Falcons": (167, 25, 48), 
               "Panthers": (0, 133, 202), "Saints": (211, 188, 141), "Buccaneers": (213, 10, 10), 
               "Cardinals": (151, 35, 63), "Rams": (0, 53, 148), "49ers": (170, 0, 0),
               "Seahawks": (0, 34, 68)}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///madden_stats.db"
db = SQLAlchemy(app)

conn = sqlite3.connect("madden_stats.db")
cur = conn.cursor()
cur.execute("select * from stats")
rows = cur.fetchall()

# Get column names from cursor.description
column_names = [desc[0] for desc in cur.description]


def create_dict(data):
    # Create a list of dictionaries where keys are column names
    result = []

    for row in data:
        row_dict = {}
        for i, value in enumerate(row):
            row_dict[column_names[i]] = value
        result.append(row_dict)

    return result


# create a data frame of all data in stats table
all_results_df = pd.DataFrame(create_dict(rows))

# temporary, team_name will have to be grabbed from drop down
team_name = "Patriots"


# temporary, needs to come from selection
stat_for_box_chart = "impactBlocking"

#stat_for_bar_chart = "throwUnderPressure"
player1 = "Patrick Mahomes"
player2 = "Tua Tagovailoa"
stats_to_compare = ["overall", 
                    "speed", 
                    "throwPower", 
                    "throwAccuracyDeep", 
                    "throwOnTheRun",
                    "playAction", 
                    "breakSack",
                    "leadBlock",
                    "passBlockFinesse"]


def player_comp(player1, player2, stats_to_compare):
    player1_data = all_results_df[all_results_df["fullNameForSearch"] == player1]
    player2_data = all_results_df[all_results_df["fullNameForSearch"] == player2]

    # Create a DataFrame for the selected statistics
    comparison_data = pd.DataFrame({
        "statistic": stats_to_compare,
        player1: player1_data[stats_to_compare].values[0],
        player2: player2_data[stats_to_compare].values[0]
    })

    fig = px.bar(
        comparison_data,
        x="statistic",  # Use "statistic" column as x-axis
        y=[player1, player2],  # Use player names as y-values
        title="Player Comparison",
        barmode="group",  # Grouped bars
        category_orders={"statistic": stats_to_compare}  # Ensure the order of statistics
    )

    fig.update_layout(legend_title_text="")

    return fig


@app.route("/")
def query_db():

    fig1 = go.Figure(data=[
    go.Bar(
        x=all_results_df[all_results_df["team"] == team_name].head(10)["fullNameForSearch"],
        y=all_results_df[all_results_df["team"] == team_name].head(10)["overall"],
        marker_color=f"rgb{team_colors[team_name]}",  # Set the bar color to red
        )
    ])

    fig1.update_layout(
        title=f"{team_name} Top 10 Overall Players",
        xaxis_title="Player",
        yaxis_title="Overall Rating",
    )
    
    chart_json_bar = fig1.to_json()


    fig2 = px.box(all_results_df, 
                  x="position", 
                  y=stat_for_box_chart, 
                  title=f"{stat_for_box_chart} Rating by Position",
                  color="position",
                  color_discrete_sequence=px.colors.qualitative.Set1,)
    chart_json_box = fig2.to_json()
     
    fig3 = player_comp(player1=player1, player2=player2, stats_to_compare=stats_to_compare)
    chart_json_comp = fig3.to_json()

    return render_template("chart.html", 
                           chart_json_bar=chart_json_bar, 
                           chart_json_box=chart_json_box,
                           chart_json_comp=chart_json_comp,
                           #chart_json_comp_2=chart_json_comp_2
                           )




if __name__ == "__main__":
    app.run(debug=True)


